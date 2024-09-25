import numpy as np

import evals
from evals.api import CompletionFn
from evals.elsuite import utils
from evals.record import RecorderBase
import evaluate

import evals.record
class Match(evals.Eval):
    def __init__(
        self,
        completion_fns: list[CompletionFn],
        samples_jsonl: str,
        *args,
        max_tokens: int = 4096,
        
        **kwargs,
    ):
        super().__init__(completion_fns, *args, **kwargs)
        assert len(completion_fns) == 1, "FuzzyMatch only supports one completion fn"
        self.max_tokens = max_tokens
        self.samples_jsonl = samples_jsonl

        
    def eval_sample(self, test_sample, rng):

        assert isinstance(test_sample, dict), "sample must be a dict"
        assert "input" in test_sample, "sample must have an 'input' key"
        assert "ideal" in test_sample, "sample must have an 'ideal' key"

        prompt, correct_answers = test_sample["input"], test_sample["ideal"]
        if not isinstance(correct_answers, list):
            correct_answers = [correct_answers]
        
        # result = self.completion_fn(
        #     prompt=prompt,
        #     temperature=0.0,  # Q: why are these hardcoded?
        #     max_tokens=self.max_tokens,
        # )

        result = self.call_completion_fn(prompt = prompt, temperature = 0., max_completion_tokens = 4096, expected = correct_answers[0])
        sampled = result.get_completions()[0]

        matches = [utils.fuzzy_match(sampled, correct_answer) for correct_answer in correct_answers]


        nlp_metrics = self.computer_nlp_metrics(sampled, correct_answers, rng=rng)
                
        evals.record.record_metrics(
            accuracy = float(True in matches),
            **nlp_metrics,
        )
        

    def call_completion_fn(self, prompt, temperature, max_completion_tokens, expected):
        return self.completion_fn(prompt=prompt, temperature=temperature, max_completion_tokens=max_completion_tokens, expected = expected)
    def computer_nlp_metrics(self, sampled, correct_answers, rng):
        f1_score, precision, recall = utils.f1_score_precision_recall(sampled, correct_answers)
        bleu = evaluate.load("bleu", experiment_id = "rng")
        rouge = evaluate.load("rouge", experiment_id = "rng")
        # mauve = evaluate.load("mauve", experiment_id = "rng", keep_in_memory=True)
        rouge_results = rouge.compute(predictions=[sampled], references=[correct_answers])
        try:
            bleu1_score = bleu.compute(predictions=[sampled], references=[correct_answers], max_order=1)['bleu']
        except:
            bleu1_score = 0
        try:
            bleu2_score = bleu.compute(predictions=[sampled], references=[correct_answers], max_order=2)['bleu']
        except:
            bleu2_score = 0
        try:
            bleu3_score = bleu.compute(predictions=[sampled], references=[correct_answers], max_order=3)['bleu']
        except:
            bleu3_score = 0
        try:
            bleu4_score = bleu.compute(predictions=[sampled], references=[correct_answers], max_order=4)['bleu']
        except:
            bleu4_score = 0
            

        # mauve_result = mauve.compute(predictions=[sampled], references=correct_answers, device_id=0)

        return {
            "f1_score": f1_score,
            'precision': precision,
            'recall': recall,
            "bleu1_score": bleu1_score,
            "bleu2_score": bleu2_score,
            "bleu3_score": bleu3_score,
            "bleu4_score": bleu4_score,
            "rouge1_scores": rouge_results['rouge1'],
            "rouge2_scores": rouge_results['rouge2'],
            "rougeL_scores": rouge_results['rougeL'],
            "rougeLsum_scores": rouge_results['rougeLsum'],
            
            # "mauve": mauve_result.mauve,
        }
    def run(self, recorder: RecorderBase):
        mauve = evaluate.load("mauve", keep_in_memory=True)
        
        samples = self.get_samples()
        self.eval_all_samples(recorder, samples)
        sampled_expected_list = recorder.get_sampling()
        sampled = sampled_expected_list[0]
        expected = sampled_expected_list[1]
        print(len(sampled), len(expected))
        mauve_result = mauve.compute(predictions=sampled, references=expected, device_id=0)
        print(mauve_result.mauve)
        try:
            scores = {key: np.mean(values) for key, values in recorder.get_scores().items()}
        except Exception as e:
            for key, values in recorder.get_scores().items():
                print(key, values)
                raise e
        scores["mauve"] = mauve_result.mauve
        
        return scores
