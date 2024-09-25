from loguru import logger
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
import json
from tqdm import tqdm
import multiprocessing as mp

useful_prompt = "Please summary the above question and reasoning and provide a detailed explanation of the final answer."

def _log_when_fail(retry_state):
    logger.info(
        "Request failed. Current retry attempts:{}. Sleep for {:.2f}. Exception: {}".format(
            retry_state.attempt_number, retry_state.idle_for, repr(retry_state.outcome.exception())
        )
    )


def _get_keys(dicts):
    keys = [set(dict_.keys()) for dict_ in dicts]
    assert all([i == j for i, j in zip(keys[1:], keys[:-1])]), keys

    return keys[0]


def dict_mean(dicts):
    keys = _get_keys(dicts)
    result = {}
    for k in keys:
        result[k] = sum([dict_[k] for dict_ in dicts]) / len(dicts)
    return result


def dict_sum(dicts):
    keys = _get_keys(dicts)
    result = {}
    for k in keys:
        result[k] = sum([dict_[k] for dict_ in dicts])
    return result


def dict_max(dicts):
    keys = _get_keys(dicts)
    result = {}
    for k in keys:
        result[k] = max([dict_[k] for dict_ in dicts])
    return result


def dict_min(dicts):
    keys = _get_keys(dicts)
    result = {}
    for k in keys:
        result[k] = min([dict_[k] for dict_ in dicts])
    return result


def compute_usage(response):
    usage = response.usage.to_dict()
    input = usage["prompt_tokens"]
    reasoning = usage["completion_tokens_details"]["reasoning_tokens"]
    output = usage["completion_tokens"] - usage["completion_tokens_details"]["reasoning_tokens"]

    cost = {
        "input": input * 15 / 10 ** 6,
        "reasoning": reasoning * 60 / 10 ** 6,
        "output": output * 60 / 10 ** 6,
    }

    cost["total"] = sum(cost.values())

    return {"input": input, "reasoning": reasoning, "output": output}, cost


@retry(
    wait=wait_random_exponential(min=1, max=60),
    before_sleep=_log_when_fail
)
def completion_retry(content):
    response = client.chat.completions.create(
        # model="o1-preview",
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        max_completion_tokens=2048,
        temperature=1
    )

    return response


def inference_one(sample):
    # content = sample["content"]
    content = sample['input'][0]["content"]
    response = completion_retry(content)
    token_usage, cost = compute_usage(response)
    response = response.to_dict()
    # make useful
    u_prompt = f"# Question\n{content}\n# Answer\n{response['choices'][0]['message']['content']}\n\n{useful_prompt}"
    u_response = completion_retry(u_prompt)
    token_usage, cost = compute_usage(u_response)
    u_response = u_response.to_dict()

    results = {"response": response, 'useful': u_response, "input": content, "meta": {"token_usage": token_usage, "cost": cost}}

    # with open("results_pubmedqa.jsonl", mode="w") as f:
    #     f.write(json.dumps(results) + "\n")

    return results

def self_consistency(sample, n_sample=3):
    # __import__("ipdb").set_trace()
    content = sample['input'][0]["content"]
    samples = []
    for _ in range(n_sample):
        response = completion_retry(content)
        token_usage, cost = compute_usage(response)
        response = response.to_dict()
        samples.append(response)

    sc_prompt = f'Given the following question and the {n_sample} responses, please select the most consistent response with other responses and the question.\n\n# Question: {content}\n\n# Responses:\n\n'
    for i, sample in enumerate(samples):
        sc_prompt += f'## Response {i+1}: {sample["choices"][0]["message"]["content"]}\n\n'

    response = completion_retry(sc_prompt)
    token_usage, cost = compute_usage(response)
    response = response.to_dict()
    
    # make useful
    u_prompt = f"{sc_prompt}\n# Summary: \n{response['choices'][0]['message']['content']}\n# Useful\n{useful_prompt}"
    useful_response = completion_retry(u_prompt)
    token_usage, cost = compute_usage(useful_response)
    useful_response = useful_response.to_dict()

    results = {"response": response, "useful": useful_response, "input": sc_prompt, "meta": {"token_usage": token_usage, "cost": cost}}


    return results

def reflexion(sample, n_sample=3):
    # __import__("ipdb").set_trace()
    content = sample['input'][0]["content"]
    samples = []
    final_samples = ['' for _ in range(n_sample)]
    for i in range(n_sample):
        response = completion_retry(content)
        token_usage, cost = compute_usage(response)
        response = response.to_dict()
        samples.append(response)

    critic_prompt = f"\n\nPlease review the answer above and criticize on where might be wrong. If you are absolutely sure it is correct, output 'True' in 'correct'."
    critic_samples = []
    for i, sample in enumerate(samples):
        c_prompt = f"{content}\n## Answer:\n{sample['choices'][0]['message']['content']}\n{critic_prompt}"
        final_samples[i] = f"\n## Original Answer:\n{sample['choices'][0]['message']['content']}\n{critic_prompt}"
        c_sample = completion_retry(c_prompt)
        token_usage, cost = compute_usage(c_sample)
        c_sample = c_sample.to_dict()
        critic_samples.append(c_sample)
        final_samples[i] += f"\n## Critic:\n{c_sample['choices'][0]['message']['content']}\n"

    reflexion_prompt = f'\n\nGiven previous attempts and feedback, carefully consider where you could go wrong in your latest attempt. Using insights from previous attempts, try to solve the task better. '
    reflex_samples = []
    for i, c_sample in enumerate(critic_samples):
        r_prompt = f"{content}\n{final_samples[i]}\n{reflexion_prompt}"
        final_samples[i] += f"\n{reflexion_prompt}"
        r_sample = completion_retry(r_prompt)
        token_usage, cost = compute_usage(r_sample)
        r_sample = r_sample.to_dict()
        reflex_samples.append(r_sample)
        final_samples[i] += f"\n## Reflexion:\n{r_sample['choices'][0]['message']['content']}\n"
        
    summary_prompt = f'\n\nPlease summarize the previous attempts and feedbacks and provide a final answer.'
    temp = ''
    for i, r_sample in enumerate(reflex_samples):
        temp += f"\n# Response {i+1}: {final_samples[i]}\n\n"
    summary_prompt = f"{content}\n{temp}\n{summary_prompt}"
    response = completion_retry(summary_prompt)
    token_usage, cost = compute_usage(response)
    response = response.to_dict()
    
    u_prompt = f"{summary_prompt}\n# Summary: \n{response['choices'][0]['message']['content']}\n\n# Useful\n{useful_prompt}"
    u_response = completion_retry(u_prompt)
    token_usage, cost = compute_usage(u_response)
    u_response = u_response.to_dict()

    results = {"response": response, 'useful': u_response, "input": summary_prompt, "meta": {"token_usage": token_usage, "cost": cost}}

    return results


def read_jsonl(path):
    lst = []
    with open(path, mode="r") as f:
        for line in tqdm(f.readlines()):
            lst.append(json.loads(line))

    return lst


def dump_jsonl(lst, path):
    with open(path, mode="w") as f:
        for sample in lst:
            f.write(json.dumps(sample) + "\n")


if __name__ == "__main__":
    client = openai.OpenAI(
        organization="org-5fz09SUguUCh5xbxXn9cFVEw",
        api_key="sk-T1u4J6uteZgxWfmCqNXfa3N6Fu6YIJQ_yIM4OUbslCT3BlbkFJAJJdLbYCewMTA0tb5YQCaFpfU007uVcsv_nJmSb6sA"
    )

    data = read_jsonl("/workspace/evals/evals/registry/data/pubmedqa/pubmedqa_sample.jsonl")

    with mp.Pool(processes=8) as pool:
        results = list(tqdm(pool.map(inference_one, data), total=len(data)))
    dump_jsonl(results, "inference_results_pubmedqa.jsonl")

    with mp.Pool(processes=8) as pool:
        results = list(tqdm(pool.map(self_consistency, data), total=len(data)))
    dump_jsonl(results, "sc_results_pubmedqa.jsonl")

    with mp.Pool(processes=8) as pool:
        results = list(tqdm(pool.map(reflexion, data), total=len(data)))
    dump_jsonl(results, "reflexion_results_pubmedqa.jsonl")
    