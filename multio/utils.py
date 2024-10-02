from __future__ import annotations

import os
from contextlib import ContextDecorator

from .plans import Config

FILE = os.PathLike


class MultioPlan(ContextDecorator):
    """
    Context manager to set multio plans
    """

    _prior_plan = None
    _plan = None

    _environ_var = "MULTIO_PLANS"

    def __init__(self, plan: FILE | dict | Config):
        """
        Create the MultioPlan context manager

        Parameters
        ----------
        plan : FILE | dict | Config
            Multio plan to be set, can be
            - a file path
            - a dictionary
            - a Config instance
            - a YAML string
            - a JSON string
        """
        self._environ_var = "MULTIO_PLANS"

        if isinstance(plan, dict):
            self._plan = Config(**plan)
        elif isinstance(plan, str):
            methods = [
                Config.from_yamlfile,
                Config.from_yaml,
                Config.model_validate,
                Config.model_validate_json,
            ]
            for method in methods:
                try:
                    self._plan = method(plan)
                    break
                except Exception:
                    pass

            if self._plan is None:
                raise ValueError(f"Invalid plan, could not parse {plan}")

        elif isinstance(plan, Config):
            self._plan = plan

    def set_plan(self):
        self._prior_plan = os.environ.get(self._environ_var, None)
        os.environ[self._environ_var] = self._plan.dump_json()

    def revert_plan(self):
        if self._prior_plan is not None:
            os.environ[self._environ_var] = self._prior_plan
        elif self._environ_var in os.environ:
            del os.environ[self._environ_var]

    def __enter__(self):
        self.set_plan()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.revert_plan()
