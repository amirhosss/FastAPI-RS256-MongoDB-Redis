from typing import Any
from datetime import timedelta

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    status,
    BackgroundTasks,
    Depends,
    Response
)
from pydantic import EmailStr

import crud
from utils import util
from utils.sending_email import send_verification_email
from utils.redis import redis
from core.security import create_jwt_token
from core.config import settings
from api.dependencies.get_user import GetUser, refresh_token_required

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post('/login')
async def authenticate_user(
    device: str,
    background_task: BackgroundTasks,
    response: Response,
    email: EmailStr = Form(...),
    password: str = Form(..., regex=settings.PASSWORD_REGEX)
) -> Any:
    if device in settings.SERVER_DEVICES:
        user = await crud.user.authenticate(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Incorrect email or password'
            )
        elif not user.is_active:
            await util.check_request_counter(user)
            token = create_jwt_token(user.public_id, 'verification')
            background_task.add_task(
                send_verification_email,
                user.name,
                email,
                token

            )
            return {
                'detail': 'An email sent to your accunt, you have 5 minutes to verify.'
            }
            
        access_token = create_jwt_token(user.public_id, 'access')
        refresh_token = create_jwt_token(user.public_id, 'refresh')

        if device == 'web':
            response.set_cookie('access_token', access_token, httponly=True)
            response.set_cookie('refresh_token', refresh_token, httponly=True)
            return {
                'detail': 'The user authenticated successfully',
                'public_id': user.public_id,
            }
        elif device == 'mobile':
            return{
                'detail': 'The user authenticated successfully',
                'public_id': user.public_id,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Device is wrong'
    )


@router.get('/verification')
async def verify_user(token: str):
    token_obj = GetUser(token, 'verification')
    user = await token_obj.get_current_user()
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The User had been already activated.'
        )

    await redis.setex(
        str(token_obj.token_data.jti),
        timedelta(minutes=settings.VERIFICATION_TOKEN_EXPIRE_MINUTES),
        'true'
    )

    await crud.user.update({'is_active': True}, user.public_id)
    
    return {'detail': 'The user activated successfully'}
    

@router.post('/refresh-token')
async def refresh_token(
    device: str,
    response: Response,
    token: str = Depends(refresh_token_required)
):
    if device in settings.SERVER_DEVICES:
        token_obj = GetUser(token, 'refresh')
        user = await token_obj.get_current_user()

        new_access_token = create_jwt_token(user.public_id, 'access')

        if device == 'web':
            response.set_cookie('access_token', new_access_token, httponly=True)
            return {
                'detail': 'The access token refreshed successfully'
            }
        elif device == 'mobile':
            return{
                'detail': 'The access token refreshed successfully',
                'access_token': new_access_token
            }
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Device is wrong'
    )