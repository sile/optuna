import hashlib
from typing import List  # NOQA

from optuna.pruners.base import BasePruner
from optuna.pruners.successive_halving import SuccessiveHalvingPruner


class HyperbandPruner(BasePruner):

    """Pruner using an asynchronous version of Hyperband Algorithm."""

    def __init__(self, min_resource=1, reduction_factor=3,
                 min_early_stopping_rate_low=0, min_early_stopping_rate_high=4):
        self.pruners = []
        self.total_priority = 0

        for i in range(min_early_stopping_rate_low, min_early_stopping_rate_high + 1):
            priority = reduction_factor ** (1 + min_early_stopping_rate_high - i)
            pruner = InnerPruner(min_resource=min_resource,
                                 priority=priority,
                                 reduction_factor=reduction_factor, min_early_stopping_rate=i)
            self.pruners.append(pruner)
            self.total_priority += priority

    def prune(self, storage, study_id, trial_id, step):
        h = hashlib.sha256()
        h.update("{}_{}".format(study_id, trial_id).encode('utf-8'))
        d = h.digest()
        n = ((d[0] << 24) + (d[1] << 16) + (d[2] << 8) + d[3]) % self.total_priority
        for i in range(len(self.pruners)):
            n -= self.pruners[i].priority
            if n <= 0:
                return self.pruners[i].prune(storage, study_id, trial_id, step)


class InnerPruner(BasePruner):
    def __init__(self, min_resource, reduction_factor, min_early_stopping_rate, priority):
        self.pruner = SuccessiveHalvingPruner(min_resource=min_resource,
                                              reduction_factor=reduction_factor,
                                              min_early_stopping_rate=min_early_stopping_rate)
        self.priority = priority

    def prune(self, storage, study_id, trial_id, step):
        return self.pruner.prune(storage, study_id, trial_id, step)
