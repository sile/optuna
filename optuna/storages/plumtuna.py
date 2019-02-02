from datetime import datetime
import json
from typing import Any  # NOQA
from typing import Dict  # NOQA
from typing import List  # NOQA
from typing import Optional  # NOQA
import urllib.request
import uuid

from optuna import distributions  # NOQA
from optuna.storages import base
from optuna.storages.base import DEFAULT_STUDY_NAME_PREFIX
from optuna import structs


class PlumtunaStorage(base.BaseStorage):
    def __init__(self):

        pass

    def _get(self, path):
        req = urllib.request.Request('http://localhost:7363{}'.format(path))
        with urllib.request.urlopen(req) as res:
            assert res.status is 200, res.reason
            return json.loads(res.read().decode())

    def _post(self, path, body=None):
        if body is None:
            req = urllib.request.Request('http://localhost:7363{}'.format(path), method='POST')
        else:
            req = urllib.request.Request('http://localhost:7363{}'.format(path), json.dumps(body).encode())
        with urllib.request.urlopen(req) as res:
            assert res.status is 200, res.reason
            return json.loads(res.read().decode())

    def _put(self, path, body):
        req = urllib.request.Request('http://localhost:7363{}'.format(path), json.dumps(body).encode(), method='PUT')
        with urllib.request.urlopen(req) as res:
            assert res.status is 200, res.reason
            return json.loads(res.read().decode())

    def create_new_study_id(self, study_name=None):
        # type: (Optional[str]) -> int

        if study_name is None:
            study_uuid = str(uuid.uuid4())
            study_name = DEFAULT_STUDY_NAME_PREFIX + study_uuid

        res = self._post('/studies', {'study_name': study_name})
        return res['study_id']

    def set_study_user_attr(self, study_id, key, value):
        # type: (int, str, Any) -> None

        self._put('/studies/{}/user_attrs/{}'.format(study_id, key), value)

    def set_study_direction(self, study_id, direction):
        # type: (int, structs.StudyDirection) -> None

        if direction == structs.StudyDirection.NOT_SET:
            d = "NOT_SET"
        elif direction == structs.StudyDirection.MINIMIZE:
            d = "MINIMIZE"
        else:
            d = "MAXIMIZE"

        self._put('/studies/{}/direction'.format(study_id), d)

    def set_study_system_attr(self, study_id, key, value):
        # type: (int, str, Any) -> None

        self._put('/studies/{}/system_attrs/{}'.format(study_id, key), value)

    # Basic study access

    def get_study_id_from_name(self, study_name):
        # type: (str) -> int

        res = self._get('/study_names/{}'.format(study_name))
        return res['study_id']

    def get_study_name_from_id(self, study_id):
        # type: (int) -> str

        res = self._get('/studies/{}'.format(study_id))
        return res['study_name']

    def get_study_direction(self, study_id):
        # type: (int) -> structs.StudyDirection

        d = self._get('/studies/{}/direction'.format(study_id))
        if d is 'NOT_SET':
            return structs.StudyDirection.NOT_SET
        elif d is 'MINIMIZE':
            return structs.StudyDirection.MINIMIZE
        else:
            return structs.StudyDirection.MAXIMIZE

    def get_study_user_attrs(self, study_id):
        # type: (int) -> Dict[str, Any]

        return self._get('/studies/{}/user_attrs'.format(study_id))

    def get_study_system_attrs(self, study_id):
        # type: (int) -> Dict[str, Any]

        return self._get('/studies/{}/system_attrs'.format(study_id))

    def get_all_study_summaries(self):
        # type: () -> List[structs.StudySummary]

        return self._get('/studies')

    # Basic trial manipulation

    def create_new_trial_id(self, study_id):
        # type: (int) -> int

        return self._post('/studies/{}/trials'.format(study_id))

    def set_trial_state(self, trial_id, state):
        # type: (int, structs.TrialState) -> None

        s = trial_state_to_json(state)
        self._put('/trials/{}/state'.format(trial_id), s)

    def set_trial_param(self, trial_id, param_name, param_value_internal, distribution):
        # type: (int, str, float, distributions.BaseDistribution) -> bool

        self._put('/trials/{}/params/{}'.format(trial_id, param_name),
                  {'value': param_value_internal,
                   'distribution': distributions.distribution_to_json(distribution)})
        return True

    def get_trial_param(self, trial_id, param_name):
        # type: (int, str) -> float

        return self._get('/trials/{}/params/{}'.format(trial_id, param_name))

    def set_trial_value(self, trial_id, value):
        # type: (int, float) -> None

        self._put('/trials/{}/value'.format(trial_id), value)

    def set_trial_intermediate_value(self, trial_id, step, intermediate_value):
        # type: (int, int, float) -> bool

        self._put('/trials/{}/intermediate_values/{}'.format(trial_id, step), intermediate_values)
        return True

    def set_trial_user_attr(self, trial_id, key, value):
        # type: (int, str, Any) -> None

        self._put('/trials/{}/user_attrs/{}'.format(trial_id, key), value)

    def set_trial_system_attr(self, trial_id, key, value):
        # type: (int, str, Any) -> None

        self._put('/trials/{}/system_attrs/{}'.format(trial_id, key), value)

    # Basic trial access

    def get_trial(self, trial_id):
        # type: (int) -> structs.FrozenTrial

        return self._get('/trials/{}'.format(trial_id)

    def get_all_trials(self, study_id):
        # type: (int) -> List[structs.FrozenTrial]

        return self._get('/studies/{}/trials'.format(study_id))

    def get_n_trials(self, study_id, state=None):
        # type: (int, Optional[structs.TrialState]) -> int

        if state is None:
            return self._get('/studies/{}/n_trials'.format(study_id))
        else:
            return self._get('/studies/{}/n_trials?state={}'.format(study_id, trial_state_to_json(state)))


def trial_state_to_json(state):
    if state is structs.TrialState.RUNNING:
        return 'RUNNING'
    elif state is structs.TrialState.COMPLETE:
        return 'COMPLETE'
    elif state is structs.TrialState.PRUNED:
        return 'PRUNED'
    else:
        return 'FAIL'
