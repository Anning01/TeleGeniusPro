from typing import Dict

from pydantic import BaseModel, field_validator, Field


class UserDataValidator(BaseModel):
    """
        Force the verification of the user's JSON format
        {
            "user_id": "1",
            "username": "john",
            ...
        }
    """
    data: Dict[str, str] = Field(..., examples=[{
        "user_id": "1",
        "username": "john"
    }, [{
        "user_id": "1",
        "username": "john"
    }, {
        "user_id": "2",
        "username": "Anna"
    }, ]
    ], description="user data")

    @field_validator('data')
    def validate_data(cls, v):
        if 'user_id' not in v:
            raise ValueError("The user_id must be included in the data")
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
