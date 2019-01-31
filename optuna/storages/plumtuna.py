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
            assert res.status is 200
            return json.loads(res.read().decode())

    def _post(self, path, body):
        req = urllib.request.Request('http://localhost:7363{}'.format(path), json.dumps(body).encode())
        with urllib.request.urlopen(req) as res:
            assert res.status is 200
            return json.loads(res.read().decode())

    def _put(self, path, body):
        req = urllib.request.Request('http://localhost:7363{}'.format(path), json.dumps(body).encode(), method='PUT')
        with urllib.request.urlopen(req) as res:
            assert res.status is 200
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

        raise NotImplementedError

    def set_study_direction(self, study_id, direction):
        # type: (int, structs.StudyDirection) -> None

        raise NotImplementedError

    def set_study_system_attr(self, study_id, key, value):
        # type: (int, str, Any) -> None

        self._put('/studies/{}/system_attrs/{}'.format(study_id, key), value)

    # Basic study access

    def get_study_id_from_name(self, study_name):
        # type: (str) -> int

        raise NotImplementedError

    def get_study_name_from_id(self, study_id):
        # type: (int) -> str

        res = self._get('/studies/{}'.format(study_id))
        return res['study_name']

    def get_study_direction(self, study_id):
        # type: (int) -> structs.StudyDirection

        raise NotImplementedError

    def get_study_user_attrs(self, study_id):
        # type: (int) -> Dict[str, Any]

        raise NotImplementedError

    def get_study_system_attrs(self, study_id):
        # type: (int) -> Dict[str, Any]

        raise NotImplementedError

    def get_all_study_summaries(self):
        # type: () -> List[structs.StudySummary]

        raise NotImplementedError

    # Basic trial manipulation

    def create_new_trial_id(self, study_id):
        # type: (int) -> int

        raise NotImplementedError

    def set_trial_state(self, trial_id, state):
        # type: (int, structs.TrialState) -> None

        raise NotImplementedError

    def set_trial_param(self, trial_id, param_name, param_value_internal, distribution):
        # type: (int, str, float, distributions.BaseDistribution) -> bool

        raise NotImplementedError

    def get_trial_param(self, trial_id, param_name):
        # type: (int, str) -> float

        raise NotImplementedError

    def set_trial_value(self, trial_id, value):
        # type: (int, float) -> None

        raise NotImplementedError

    def set_trial_intermediate_value(self, trial_id, step, intermediate_value):
        # type: (int, int, float) -> bool

        raise NotImplementedError

    def set_trial_user_attr(self, trial_id, key, value):
        # type: (int, str, Any) -> None

        raise NotImplementedError

    def set_trial_system_attr(self, trial_id, key, value):
        # type: (int, str, Any) -> None

        raise NotImplementedError

    # Basic trial access

    def get_trial(self, trial_id):
        # type: (int) -> structs.FrozenTrial

        raise NotImplementedError

    def get_all_trials(self, study_id):
        # type: (int) -> List[structs.FrozenTrial]

        raise NotImplementedError

    def get_n_trials(self, study_id, state=None):
        # type: (int, Optional[structs.TrialState]) -> int

        raise NotImplementedError
