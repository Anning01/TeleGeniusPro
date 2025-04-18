from typing import Dict

from pydantic import BaseModel, field_validator


class UserDataValidator(BaseModel):
    """
        Force the verification of the user's JSON format
        {
            "username": "john",
            ...
        }
    """
    data: Dict[str, str]

    @field_validator('data')
    def validate_data(cls, v):
        for key, value in v.items():
            if not key:  # Check for empty strings
                raise ValueError("All keys must be non-empty strings")
            if not value:
                raise ValueError("All values must be non-empty strings")
            if len(key) > 100:
                raise ValueError("Keys must not exceed 100 characters")
            if len(value) > 100:
                raise ValueError("Values must not exceed 100 characters")
        return v
