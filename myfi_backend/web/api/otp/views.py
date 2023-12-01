import uuid

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from redis.asyncio import ConnectionPool

from myfi_backend.services.redis.dependency import get_redis_pool
from myfi_backend.utils.redis import REDIS_HASH_NEW_USER, get_from_redis, set_to_redis
from myfi_backend.web.api.otp.schema import OtpDTO, OtpResponseDTO, UserDTO

router = APIRouter()


def generate_otp() -> str:
    """Generates a 4-digit OTP and returns it as an integer.

    :returns: A 4-digit OTP.
    """
    return "432100"


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
    # generate temp user id
    user.user_id = uuid.uuid4()
    if user.email:
        # send email OTP
        otp = generate_otp()
        user_otp = OtpDTO(user=user, email_otp=otp)
        await set_to_redis(
            redis_pool=redis_pool,
            key=str(user.user_id),
            value=user_otp.json(),
            hash_key=REDIS_HASH_NEW_USER,
        )
        # send email with OTP
    elif user.mobile:
        # send mobile OTP
        otp = generate_otp()
        user_otp = OtpDTO(user=user, mobile_otp=otp)
        await set_to_redis(
            redis_pool=redis_pool,
            key=str(user.user_id),
            value=user_otp.json(),
            hash_key=REDIS_HASH_NEW_USER,
        )
        # send SMS with OTP
    else:
        raise HTTPException(status_code=400, detail="Invalid request.")
    return OtpResponseDTO(user_id=user.user_id, message="SUCCESS.")


@router.post("/verify/", response_model=OtpResponseDTO)
async def verify(  # noqa: WPS231
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
    if otp.user.user_id:
        try:
            value = await get_from_redis(
                redis_pool=redis_pool,
                key=str(otp.user.user_id),
                hash_key=REDIS_HASH_NEW_USER,
            )
            if value:
                user_otp = OtpDTO.parse_raw(value)
                if verify_otp(otp, user_otp):
                    return OtpResponseDTO(user_id=otp.user.user_id, message="SUCCESS.")
            else:
                raise HTTPException(status_code=400, detail="Invalid request.")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid request.")

    raise HTTPException(status_code=404, detail="Not Found.")


def verify_otp(
    otp: OtpDTO,
    user_otp: OtpDTO,
) -> bool:
    """
    Verify OTP for mobile or email.

    :param otp: OTP object containing email or mobile number and OTP.
    :param user_otp: OTP object from db.
    :returns: True if OTP verification success, False otherwise.
    """
    if otp.user.mobile and verify_mobile_otp(otp, user_otp):
        return True
    elif otp.user.email and verify_email_otp(otp, user_otp):
        return True
    return False


def verify_mobile_otp(
    otp: OtpDTO,
    user_otp: OtpDTO,
) -> bool:
    """
    Verify OTP for mobile.

    :param otp: OTP object containing email or mobile number and OTP.
    :param user_otp: OTP object from db.
    :returns: True if OTP verification for mobile success, False otherwise.
    """
    if (user_otp.user.mobile == otp.user.mobile) and (
        user_otp.mobile_otp == otp.mobile_otp
    ):
        return True
    return False


def verify_email_otp(
    otp: OtpDTO,
    user_otp: OtpDTO,
) -> bool:
    """
    Verify OTP for email.

    :param otp: OTP object containing email or mobile number and OTP.
    :param user_otp: OTP object from db.
    :returns: True if OTP verification for email success, False otherwise.
    """
    if (user_otp.user.email == otp.user.email) and (
        user_otp.email_otp == otp.email_otp
    ):
        return True
    return False
