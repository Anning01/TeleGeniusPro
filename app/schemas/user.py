from typing import Dict
from faker import Faker
from pydantic import BaseModel, field_validator, Field

fake = Faker(["zh_CN"])


class UserDataValidator(BaseModel):
    """
    Force the verification of the user's JSON format
    {
        "user_id": "1",
        "username": "john",
        ...
    }
    """

    data: Dict[str, str] = Field(
        ...,
        examples=[
            {"user_id": "1", "username": "john"},
            [
                {"user_id": "1", "username": "john"},
                {"user_id": "2", "username": "Anna"},
            ],
        ],
        description="user data",
    )

    @field_validator("data")
    def validate_data(cls, v):
        if "user_id" not in v:
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

    @classmethod
    def generate_fake_user(cls) -> Dict[str, str]:
        """Generate virtual user data"""
        return {
            "user_id": str(fake.random_number(digits=6)),
            "nick_name": fake.name(),
            "mobile_phone": fake.phone_number(),
            "username": fake.user_name(),
            "country": fake.country(),
            "last_name": fake.last_name(),
            "age": str(fake.random_int(min=18, max=80)),
            "gender": fake.random_element(elements=("male", "female")),
            "interested": fake.random_element(elements=("single", "married")),
            "email": fake.email(),
            "hobbies": fake.random_element(
                elements=("reading", "gaming", "sports", "music", "travel")
            ),
            "job": fake.job(),
            "income": str(fake.random_int(min=5000, max=50000)),
            "remark": fake.sentence(),
        }
