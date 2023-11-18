from typing import Dict

from fastapi import APIRouter

from fastapi_backend.web.api.otp.schema import (
    OtpDTO,
    SignupResponseDTO,
    UserDTO,
    VerifyResponseDTO,
)

router = APIRouter()

otp_dict: Dict[str, int] = {}


def generate_otp() -> int:
    """Generates a 4-digit OTP and returns it as an integer.

    :returns: A 4-digit OTP.
    """
    return 4321


@router.post("/signup/", response_model=SignupResponseDTO)
async def signup(user: UserDTO) -> SignupResponseDTO:
    """Sends OTP to the user's email or mobile number.

    :param user: User object containing email or mobile number and password.
    :returns: Dictionary containing success message.
    """
    if user.email:
        # send email OTP
        otp = generate_otp()
        otp_dict[user.email] = otp
        # send email with OTP
    elif user.mobile:
        # send mobile OTP
        otp = generate_otp()
        otp_dict[user.mobile] = otp
        # send SMS with OTP
    else:
        return SignupResponseDTO(message="Email or mobile is required.")
    return SignupResponseDTO(message="OTP sent successfully.")


@router.post("/verify/", response_model=VerifyResponseDTO)
async def verify(otp: OtpDTO) -> VerifyResponseDTO:
    """
    Verifies the OTP sent to the user's email or mobile number.

    :param otp: OTP object containing email or mobile number and OTP.
    :returns: VerifyResponse object containing success message.
    """
    if otp.email:
        key = otp.email
    elif otp.mobile:
        key = otp.mobile
    else:
        return VerifyResponseDTO(message="Email or mobile is required.")

    if key not in otp_dict:
        return VerifyResponseDTO(message=f"Invalid {key} or OTP.")
    if otp_dict[key] != otp.otp:
        return VerifyResponseDTO(message=f"Invalid {key} or OTP.")
    del otp_dict[key]  # noqa: WPS420

    return VerifyResponseDTO(message="OTP verified successfully.")
