

import evals
from evals.elsuite import utils

import evals.record
from evals.elsuite.basic.match_nlp import Match as NLPMatch
from evals.elsuite import gpt_eval
class Match(NLPMatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
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
        result = self.call_completion_fn(prompt = prompt, temperature = 1., max_completion_tokens = 4096, expected = correct_answers[0])

        sampled = result.get_completions()[0]

        matches = [utils.fuzzy_match(sampled, correct_answer) for correct_answer in correct_answers]


        nlp_metrics = self.computer_nlp_metrics(sampled, correct_answers, rng=rng)
        gpt_metrics = self.computer_gpt_metrics(prompt = prompt, sampled = sampled, correct_answers = correct_answers[0])
        evals.record.record_metrics(
            accuracy = float(True in matches),
            **nlp_metrics,
            **gpt_metrics,
        )
        
    def computer_gpt_metrics(self, prompt, sampled, correct_answers):
        return gpt_eval.get_score(prompt = prompt, result = sampled, reference = correct_answers)

