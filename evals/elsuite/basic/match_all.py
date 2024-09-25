import numpy as np

import evals
from evals.api import CompletionFn
from evals.elsuite import utils
from evals.record import RecorderBase
from evals.elsuite import gpt_eval


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
        del rng

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
        result = self.completion_fn(
            prompt=prompt,
            temperature=1.0,  # Q: why are these hardcoded?
            max_completion_tokens=4096,
        )        
        sampled = result.get_completions()[0]

        matches = [utils.fuzzy_match(sampled, correct_answer) for correct_answer in correct_answers]

        evals.record.record_match(
            True in matches,
            expected=correct_answers,
            picked=[sampled for i in range(len(correct_answers)) if matches[i]],
        )

        evals.record.record_metrics(
            accuracy = float(True in matches),
            f1_score = utils.f1_score(sampled, correct_answers),
            bleu1_score = utils.bleu_score(sampled, correct_answers, n_gram= 1),
            RougeL_score = utils.RougeL_score([sampled.split()], [[correct_answer.split() for correct_answer in correct_answers]]),
            Rouge1_score  = utils.RougeN_score([sampled.split()], [[correct_answer.split() for correct_answer in correct_answers]], n_gram= 1),
            Rouge2_score  = utils.RougeN_score([sampled.split()], [[correct_answer.split() for correct_answer in correct_answers]], n_gram= 2),
            Rouge3_score  = utils.RougeN_score([sampled.split()], [[correct_answer.split() for correct_answer in correct_answers]], n_gram= 3),
            Rouge4_score  = utils.RougeN_score([sampled.split()], [[correct_answer.split() for correct_answer in correct_answers]], n_gram= 4),
            gpt_score = gpt_eval.get_score(sampled, correct_answers[0]),
            
        )
        
        return evals.record_and_check_match(
            prompt=prompt,
            sampled=sampled,
            expected=correct_answers,
        )
        

    def run(self, recorder: RecorderBase):
        samples = self.get_samples()
        self.eval_all_samples(recorder, samples)
        RougeL_scores = recorder.get_scores("RougeL_score")
        Rouge_L_P = np.mean([score['Rouge-L-P'] for score in RougeL_scores])
        Rouge_L_R = np.mean([score['Rouge-L-R'] for score in RougeL_scores])
        Rouge_L_F = np.mean([score['Rouge-L-F'] for score in RougeL_scores])
        Rouge1_scores = recorder.get_scores("Rouge1_score")
        Rouge1_scores = np.mean([score['Rouge-1-F'] for score in Rouge1_scores])
        Rouge2_scores = recorder.get_scores("Rouge2_score")
        Rouge2_scores = np.mean([score['Rouge-2-F'] for score in Rouge2_scores])
        Rouge3_scores = recorder.get_scores("Rouge3_score")
        Rouge3_scores = np.mean([score['Rouge-3-F'] for score in Rouge3_scores])
        Rouge4_scores = recorder.get_scores("Rouge4_score")
        Rouge4_scores = np.mean([score['Rouge-4-F'] for score in Rouge4_scores])
        
        return {
            "accuracy": np.mean(recorder.get_scores("accuracy")),
            "f1_score": np.mean(recorder.get_scores("f1_score")),
            "bleu1_score": np.mean(recorder.get_scores("bleu1_score")),
            "Rouge-L-F": Rouge_L_F,
            "Rouge1_scores": Rouge1_scores,
            "Rouge2_scores": Rouge2_scores,
            "Rouge3_scores": Rouge3_scores,
            "Rouge4_scores": Rouge4_scores,
            "gpt_score": np.mean(recorder.get_scores("gpt_score")),
        }
