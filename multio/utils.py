import json
import os
from contextlib import ContextDecorator

FILE = os.PathLike


class MultioPlan(ContextDecorator):
    """
    Context manager to set multio plans
    """

    _prior_state = None
    _plan = None

    _environ_var = "MULTIO_SERVER_CONFIG_FILE"

    def __init__(self, plan: FILE | dict):
        """
        Create the MultioPlan context manager

        Parameters
        ----------
        plan : FILE | dict
            File to be set to `MULTIO_SERVER_CONFIG_FILE` or
            Dictionary to be dumped to json and set to 'MULTIO_PLANS'
        """
        if isinstance(plan, str):
            self._plan = plan
            self._environ_var = "MULTIO_SERVER_CONFIG_FILE"
        else:
            self._plan = json.dumps(plan)
            self._environ_var = "MULTIO_PLANS"

    def __enter__(self):
        self._prior_state = os.environ.get(self._environ_var, None)
        os.environ[self._environ_var] = self._plan
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._prior_state is not None:
            os.environ[self._environ_var] = self._prior_plan
        else:
            del os.environ[self._environ_var]
