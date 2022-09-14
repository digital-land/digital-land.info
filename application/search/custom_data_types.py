from pydantic import validators


class FormInt(int):
    """
    Create a custom integer type that runs the same integer validations but also transforms empty strings. this allows
    us to identify the difference between normal ints and those which can be used in forms.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="integer")

    @classmethod
    def validate(cls, v):
        if v is None or v == "":
            return None
        return validators.int_validator(v)

    def __repr__(self):
        return f"FormInt({super().__repr__()})"
