import numpy

from optuna import distributions
from optuna.samplers.base import BaseSampler


class HyperbandSampler(BaseSampler):
    def __init__(self, sampler, hyperband_pruner):
        self._sampler = sampler
        self._pruner = hyperband_pruner

    def infer_relative_search_space(self, study, trial):
        study = self._pruner._create_bracket_study(
            study, self._pruner._get_bracket_id(study, trial)
        )
        return self._sampler.infer_relative_search_space(study, trial)

    def sample_relative(self, study, trial, search_space):
        study = self._pruner._create_bracket_study(
            study, self._pruner._get_bracket_id(study, trial)
        )
        return self._sampler.sample_relative(study, trial, search_space)

    def sample_independent(self, study, trial, param_name, param_distribution):
        study = self._pruner._create_bracket_study(
            study, self._pruner._get_bracket_id(study, trial)
        )
        return self._sampler.sample_independent(study, trial, param_name, param_distribution)
