from typing import Any, Callable

from pydantic import ValidationInfo, ValidatorFunctionWrapHandler


def make_validator(
    func: Callable[[Any], Any],
) -> Callable[[Any, ValidatorFunctionWrapHandler, ValidationInfo], Any]:
    """
    Make a function acting only values and convert it into a Pydantic validator
    """

    def validator(v: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo) -> Any:
        return func(v)

    return validator
