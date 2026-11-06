from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
    model_validator
)


# Registration
class UserCreate(BaseModel):

    email: EmailStr

    password: str = Field(min_length=8, max_length=128)


# User response
class UserResponse(BaseModel):

    id: int

    email: EmailStr

    model_config = {"from_attributes": True}


# Login
class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(max_length=128)


# JWT response
class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"


# Create task
class TaskCreate(BaseModel):

    title: str = Field(min_length=1, max_length=100)

    description: str | None = Field(
        default=None,
        max_length=500
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value


# Full task update
class TaskUpdate(BaseModel):

    title: str = Field(min_length=1, max_length=100)

    description: str | None = Field(
        default=None,
        max_length=500
    )

    completed: bool

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value


# Partial task update
class TaskPatch(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):

        if value is None:
            raise ValueError("Title cannot be null")

        value = value.strip()

        if not value:
            raise ValueError("Title cannot be empty")

        return value

    @field_validator("completed")
    @classmethod
    def validate_completed(cls, value):

        if value is None:
            raise ValueError("Completed cannot be null")

        return value

    @model_validator(mode="after")
    def validate_patch(self):

        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        return self


# Task response
class TaskResponse(BaseModel):

    id: int

    title: str

    description: str | None

    completed: bool

    user_id: int

    model_config = {"from_attributes": True}