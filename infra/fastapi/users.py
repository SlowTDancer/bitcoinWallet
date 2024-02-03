from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from core.errors import UserAlreadyExistsError
from core.user import User
from infra.fastapi.dependables import UserRepositoryDependable

user_api = APIRouter(tags=["Users"])


class RegisterUserRequest(BaseModel):
    email: str


class RegisterUserResponse(BaseModel):
    api_key: UUID


class RegisterUserResponseEnvelope(BaseModel):
    user: RegisterUserResponse


@user_api.post(
    "/users",
    status_code=201,
    response_model=RegisterUserResponseEnvelope,
    responses={
        409: {
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "error": {
                                "message": "user with email: <email> already exists."
                            }
                        }
                    }
                }
            }
        }
    },
)
def register_user(
    request: RegisterUserRequest, users: UserRepositoryDependable
) -> dict[str, dict[str, UUID]] | JSONResponse:
    email = request.email
    user = User(email)
    try:
        users.create(user)
        return {"user": {"api_key": user.get_private_key()}}
    except UserAlreadyExistsError:
        return JSONResponse(
            status_code=409,
            content={
                "error": {"message": f"user with email <{email}>" " already exists."}
            },
        )
