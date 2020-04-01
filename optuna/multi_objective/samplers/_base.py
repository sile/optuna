import abc
from typing import Any
from typing import Dict

from optuna._experimental import experimental
from optuna import multi_objective
from optuna.distributions import BaseDistribution


@experimental("1.4.0")
class BaseMoSampler(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def infer_relative_search_space(
        self, study: "multi_objective.study.MoStudy", trial: "multi_objective.trial.FrozenMoTrial"
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def sample_relative(
        self,
        study: "multi_objective.study.MoStudy",
        trial: "multi_objective.trial.FrozenMoTrial",
        search_space: Dict[str, BaseDistribution],
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def sample_independent(
        self,
        study: "multi_objective.study.MoStudy",
        trial: "multi_objective.trial.FrozenMoTrial",
        param_name: str,
        param_distribution: BaseDistribution,
    ) -> Any:
        raise NotImplementedError