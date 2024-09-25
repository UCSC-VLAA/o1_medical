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
            gpt_score = gpt_eval.get_score(prompt, sampled, correct_answers[0], endpoint=endpoint),
        )
        
        return evals.record_and_check_match(
            prompt=prompt,
            sampled=sampled,
            expected=correct_answers,
        )

    def run(self, recorder: RecorderBase):
        samples = self.get_samples()
        self.eval_all_samples(recorder, samples)
        
        return {
            "gpt_score": np.mean(recorder.get_scores("gpt_score")),
        }
