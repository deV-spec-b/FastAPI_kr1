from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from .models import UserRegister, UserResponse, ErrorResponse
from .database import create_users_table, add_user, get_user_by_username


create_users_table()


app = FastAPI()


@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Некорректные данные"},
        409: {"model": ErrorResponse, "description": "Пользователь уже существует"}
    }
)
async def register(user_data: UserRegister):
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
    success = add_user(user_data.username, user_data.password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return UserResponse(
        message="User registered successfully!",
        username=user_data.username
    )