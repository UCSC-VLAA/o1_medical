import evals
from evals.elsuite import utils
from alignscore import AlignScore

import evals.record
from evals.elsuite.basic.match_nlp_gpt import Match as NLPGPTMatch
class Match(NLPGPTMatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scorer = AlignScore(model='roberta-base', batch_size=1, device='cuda:0', ckpt_path='./AlignScore/ckpt/AlignScore-large.ckpt', evaluation_mode='nli_sp')

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
        hallu_metrics = self.computer_hallu_metrics(contexts= correct_answers, claims = [sampled])
        try:
            evals.record.record_metrics(
                accuracy = float(True in matches),
                **nlp_metrics,
                **gpt_metrics,
                **hallu_metrics,
            )
        except:
            print(nlp_metrics, gpt_metrics, hallu_metrics)
        
        return evals.record_and_check_match(
            prompt=prompt,
            sampled=sampled,
            expected=correct_answers,
        )
    def computer_hallu_metrics(self, contexts, claims):
        try:
            align_score = self.scorer.score(contexts=contexts, claims=claims)
        except:
            align_score = 0
        return {"align_score":align_score}   
