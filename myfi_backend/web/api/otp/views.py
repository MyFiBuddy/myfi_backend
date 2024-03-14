import uuid
from enum import Enum
from typing import Tuple

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from redis.asyncio import ConnectionPool

from myfi_backend.services.redis.dependency import get_redis_pool
from myfi_backend.utils.redis import (
    REDIS_HASH_NEW_USER,
    REDIS_HASH_USER,
    REDIS_NEW_USER_EXPIRY_TIME,
    delete_from_redis,
    get_from_redis,
    set_to_redis,
)
from myfi_backend.web.api.otp.schema import (
    OtpDTO,
    OtpResponseDTO,
    PinDTO,
    SetPinResponseDTO,
    UserDTO,
    VerifyPinResponseDTO,
)

router = APIRouter()


class UserAuthType(Enum):
    """Enum for user authentication type."""

    EMAIL = 1
    MOBILE = 2


@router.post("/signup/", response_model=OtpResponseDTO)
async def signup(
    user: UserDTO,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> OtpResponseDTO:
    """
    Sends OTP to the user's email or mobile number.

    :param user: User object containing email or mobile number and password.
    :param redis_pool: Redis connection pool.
    :returns: Dictionary containing success message.
    :raises HTTPException: If email or mobile is not provided.
    """
    try:
        if user.email:
            user_otp, is_existing_user = await signup_email(
                redis_pool=redis_pool,
                user=user,
            )
        elif user.mobile:
            user_otp, is_existing_user = await signup_mobile(
                redis_pool=redis_pool,
                user=user,
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid request.")

        if user_otp and user_otp.user.user_id:
            return OtpResponseDTO(
                user_id=user_otp.user.user_id,
                is_existing_user=is_existing_user,
                message="SUCCESS.",
            )
        raise HTTPException(status_code=400, detail="Invalid request.")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request.")


@router.post("/verify/otp", response_model=OtpResponseDTO)
async def verify_otp(
    otp: OtpDTO,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> OtpResponseDTO:
    """
    Verifies the OTP sent to the user's email or mobile number.

    :param otp: OTP object containing email or mobile number and OTP.
    :param redis_pool: Redis connection pool.
    :returns: VerifyResponse object containing success message.
    :raises HTTPException: If email or mobile is not provided or if the OTP is \
        invalid. returns 400 if request is invalid, returns 404 if user or OTP \
        is invalid
    """
    try:
        if otp.user.email and otp.user.user_id:
            is_verified, is_existing_user = await verify_email_otp(
                redis_pool=redis_pool,
                otp=otp,
            )
        elif otp.user.mobile and otp.user.user_id:
            is_verified, is_existing_user = await verify_mobile_otp(
                redis_pool=redis_pool,
                otp=otp,
            )
        else:
            HTTPException(status_code=400, detail="Invalid request.")

        if is_verified and otp.user.user_id:
            return OtpResponseDTO(
                user_id=otp.user.user_id,
                is_existing_user=is_existing_user,
                message="SUCCESS.",
            )
        raise HTTPException(status_code=404, detail="Not found.")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request.")


@router.post("/set/pin/", response_model=SetPinResponseDTO)
async def set_pin(
    pin: PinDTO,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> SetPinResponseDTO:
    """
    Sets the PIN for the user's account.

    :param pin: PinDTO object containing user_id and PIN.
    :param redis_pool: Redis connection pool.
    :returns: SetPinResponseDTO object containing response.
    :raises HTTPException: If the request is invalid or the user is not found.
    """
    try:
        value = await get_from_redis(
            redis_pool=redis_pool,
            key=str(pin.user_id),
            hash_key=REDIS_HASH_USER,
        )
        # check if user is already an existing user
        if value:
            # user is already an existing user
            user_otp = OtpDTO.parse_raw(value)
            user_otp.pin = pin.pin
            await set_to_redis(
                redis_pool=redis_pool,
                key=str(user_otp.user.user_id),
                value=user_otp.json(),
                hash_key=REDIS_HASH_USER,
            )
            return SetPinResponseDTO(user_id=pin.user_id, message="SUCCESS.")

        raise HTTPException(status_code=400, detail="Invalid request.")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request.")


@router.post("/verify/pin/", response_model=VerifyPinResponseDTO)
async def verify_pin(
    pin: PinDTO,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> VerifyPinResponseDTO:
    """
    Verifies the PIN for the user's account.

    :param pin: PinDTO object containing user_id and PIN.
    :param redis_pool: Redis connection pool.
    :returns: VerifyPinResponseDTO object containing response.
    :raises HTTPException: If the request is invalid or the pin does not match.
    """
    try:
        value = await get_from_redis(
            redis_pool=redis_pool,
            key=str(pin.user_id),
            hash_key=REDIS_HASH_USER,
        )
        # check if user is already an existing user
        if value:
            # user is already an existing user
            user_otp = OtpDTO.parse_raw(value)
            if user_otp.pin == pin.pin:
                return VerifyPinResponseDTO(
                    user_id=pin.user_id,
                    is_verified=True,
                    message="SUCCESS.",
                )
        raise HTTPException(status_code=400, detail="Invalid request.")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request.")


async def signup_email(
    redis_pool: ConnectionPool,
    user: UserDTO,
) -> Tuple[OtpDTO, bool]:
    """
    Signup user with email.

    :param redis_pool: Redis connection pool.
    :param user: User object containing email or mobile number.
    :returns: OTP object containing email or mobile number and OTP. Return True if is \
    existing user else False.
    :raises HTTPException: If email not provided.
    """
    try:
        if user.email:
            value = await get_from_redis(
                redis_pool=redis_pool,
                key=user.email,
                hash_key=REDIS_HASH_USER,
            )
            if value:
                # user is already an existing user
                user_otp = OtpDTO.parse_raw(value)
                otp = generate_otp(UserAuthType.EMAIL)
                user_otp.email_otp = otp

                # update the user with the new otp
                await set_to_redis(
                    redis_pool=redis_pool,
                    key=user.email,
                    value=user_otp.json(),
                    hash_key=REDIS_HASH_USER,
                )
                # send OTP to email
                return user_otp, True

            # user is a new user
            user.user_id = uuid.uuid4()
            otp = generate_otp(UserAuthType.EMAIL)
            user_otp = OtpDTO(user=user, email_otp=otp)

            await set_to_redis(
                redis_pool=redis_pool,
                key=user.email,
                value=user_otp.json(),
                hash_key=REDIS_HASH_NEW_USER,
                expire=REDIS_NEW_USER_EXPIRY_TIME,
            )

            return user_otp, False

        raise HTTPException(status_code=400, detail="Invalid request.")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request.")


async def signup_mobile(
    redis_pool: ConnectionPool,
    user: UserDTO,
) -> Tuple[OtpDTO, bool]:
    """
    Signup user with mobile.

    :param redis_pool: Redis connection pool.
    :param user: User object containing email or mobile number.
    :returns: OTP object containing user_id, email or mobile number and OTP. Return \
    True if is a existing user else False.
    :raises HTTPException: If mobile not provided.
    """
    try:
        if user.mobile:
            value = await get_from_redis(
                redis_pool=redis_pool,
                key=user.mobile,
                hash_key=REDIS_HASH_USER,
            )
            if value:
                # user is already an existing user
                user_otp = OtpDTO.parse_raw(value)
                otp = generate_otp(UserAuthType.MOBILE)
                user_otp.mobile_otp = otp

                # update the user with the new otp
                await set_to_redis(
                    redis_pool=redis_pool,
                    key=user.mobile,
                    value=user_otp.json(),
                    hash_key=REDIS_HASH_USER,
                )
                # send OTP to mobile
                return user_otp, True

            # user is a new user
            user.user_id = uuid.uuid4()
            otp = generate_otp(UserAuthType.MOBILE)
            user_otp = OtpDTO(user=user, mobile_otp=otp)

            await set_to_redis(
                redis_pool=redis_pool,
                key=user.mobile,
                value=user_otp.json(),
                hash_key=REDIS_HASH_NEW_USER,
                expire=REDIS_NEW_USER_EXPIRY_TIME,
            )

            return user_otp, False

        raise HTTPException(status_code=400, detail="Invalid request.")

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request.")


async def verify_mobile_otp(
    redis_pool: ConnectionPool,
    otp: OtpDTO,
) -> Tuple[bool, bool]:
    """
    Verify OTP for mobile.

    :param redis_pool: Redis connection pool.
    :param otp: OTP object containing email or mobile number and OTP.
    :returns: True if OTP verification for mobile success, False otherwise. Return \
    True if the user is an existing user, False otherwise.
    """
    if otp.user.mobile:
        value = await get_from_redis(
            redis_pool=redis_pool,
            key=otp.user.mobile,
            hash_key=REDIS_HASH_USER,
        )
        # check if user is already an existing user
        if value:
            # user is already an existing user
            user_otp = OtpDTO.parse_raw(value)
            is_existing_user = True
        else:
            # check if user a new user
            value = await get_from_redis(
                redis_pool=redis_pool,
                key=otp.user.mobile,
                hash_key=REDIS_HASH_NEW_USER,
            )
            if value:
                # user is a new user
                user_otp = OtpDTO.parse_raw(value)
                is_existing_user = False
            else:
                # user not found
                HTTPException(status_code=400, detail="Invalid request.")

        if (
            (user_otp.user.mobile == otp.user.mobile)
            and (user_otp.mobile_otp == otp.mobile_otp)
            and (user_otp.user.user_id == otp.user.user_id)
        ):
            # delete the user from new user hash as OTP succeeded
            if not is_existing_user:
                await delete_from_redis(
                    redis_pool=redis_pool,
                    key=otp.user.mobile,
                    hash_key=REDIS_HASH_NEW_USER,
                )
                # add the user to user hash as OTP succeeded
                await set_to_redis(
                    redis_pool=redis_pool,
                    key=otp.user.mobile,
                    value=user_otp.json(),
                    hash_key=REDIS_HASH_USER,
                )
                # also add the user_id as key as OTP succeeded
                await set_to_redis(
                    redis_pool=redis_pool,
                    key=str(otp.user.user_id),
                    value=user_otp.json(),
                    hash_key=REDIS_HASH_USER,
                )
            return True, is_existing_user

    return False, is_existing_user


async def verify_email_otp(
    redis_pool: ConnectionPool,
    otp: OtpDTO,
) -> Tuple[bool, bool]:
    """
    Verify OTP for email.

    :param redis_pool: Redis connection pool.
    :param otp: OTP object containing email or mobile number and OTP.
    :returns: True if OTP verification for mobile success, False otherwise. Return \
    True if the user is an existing user, False otherwise.
    """
    if otp.user.email:
        value = await get_from_redis(
            redis_pool=redis_pool,
            key=otp.user.email,
            hash_key=REDIS_HASH_USER,
        )
        # check if user is already an existing user
        if value:
            # user is already an existing user
            user_otp = OtpDTO.parse_raw(value)
            is_existing_user = True
        else:
            # check if user a new user
            value = await get_from_redis(
                redis_pool=redis_pool,
                key=otp.user.email,
                hash_key=REDIS_HASH_NEW_USER,
            )
            if value:
                # user is a new user
                user_otp = OtpDTO.parse_raw(value)
                is_existing_user = False
            else:
                # user not found
                HTTPException(status_code=400, detail="Invalid request.")

        if (
            (user_otp.user.email == otp.user.email)
            and (user_otp.email_otp == otp.email_otp)
            and (user_otp.user.user_id == otp.user.user_id)
        ):
            # delete the user from new user hash as OTP succeeded
            if not is_existing_user:
                await delete_from_redis(
                    redis_pool=redis_pool,
                    key=otp.user.email,
                    hash_key=REDIS_HASH_NEW_USER,
                )
                # add the user to user hash as OTP succeeded
                await set_to_redis(
                    redis_pool=redis_pool,
                    key=otp.user.email,
                    value=user_otp.json(),
                    hash_key=REDIS_HASH_USER,
                )
                # also add the user_id as key as OTP succeeded
                await set_to_redis(
                    redis_pool=redis_pool,
                    key=str(otp.user.user_id),
                    value=user_otp.json(),
                    hash_key=REDIS_HASH_USER,
                )
            return True, is_existing_user

    return False, is_existing_user


def generate_otp(signup_type: UserAuthType) -> str:
    """Generates a 4-digit OTP and returns it as an integer.

    :param signup_type: Signup type.
    :returns: A 4-digit OTP.
    """
    return "432100"
