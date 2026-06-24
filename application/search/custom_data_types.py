from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic.json_schema import GetJsonSchemaHandler, JsonSchemaValue
from pydantic_core import core_schema


class FormInt(int):
    """
    Custom integer type that accepts empty strings by treating them as None.
    Used for optional integer form fields where an empty string submission is valid.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "integer"}

    @classmethod
    def validate(cls, v: Any):
        if v is None or v == "":
            return None
        return int(v)

    def __repr__(self) -> str:
        return f"FormInt({super().__repr__()})"
