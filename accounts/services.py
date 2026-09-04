import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import OTPChallenge, User


OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5


def _hash_otp(otp):
    """
    Create a SHA-256 hash of the OTP.
    The plaintext OTP is never stored in the database.
    """
    return hashlib.sha256(otp.encode()).hexdigest()


def _generate_otp():
    """
    Generate a cryptographically secure 6-digit OTP.
    """
    return f"{secrets.randbelow(1_000_000):06d}"


def request_otp(email, purpose):
    """
    Generate and send an OTP for signup or login.

    Returns:
        OTPChallenge instance and the plaintext OTP.

    The plaintext OTP is returned only so development/tests can
    inspect it. It is never stored in the database.
    """
    email = email.strip().lower()

    now = timezone.now()

    existing = (
        OTPChallenge.objects
        .filter(
            email=email,
            purpose=purpose,
            consumed_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )

    if existing:
        elapsed = (now - existing.last_sent_at).total_seconds()

        if elapsed < OTP_RESEND_COOLDOWN_SECONDS:
            remaining = int(
                OTP_RESEND_COOLDOWN_SECONDS - elapsed
            )

            raise ValueError(
                f"Please wait {remaining} seconds before requesting another OTP."
            )

    otp = _generate_otp()
    code_hash = _hash_otp(otp)

    challenge = OTPChallenge.objects.create(
        email=email,
        purpose=purpose,
        code_hash=code_hash,
        expires_at=now + timedelta(minutes=OTP_EXPIRY_MINUTES),
        attempts=0,
        max_attempts=OTP_MAX_ATTEMPTS,
        last_sent_at=now,
    )

    send_mail(
        subject="Your THE MP BLAST verification code",
        message=(
            f"Your verification code is: {otp}\n\n"
            f"This code will expire in {OTP_EXPIRY_MINUTES} minutes."
        ),
        from_email=getattr(
            settings,
            "DEFAULT_FROM_EMAIL",
            "webmaster@localhost",
        ),
        recipient_list=[email],
        fail_silently=False,
    )

    return challenge, otp


def verify_otp(email, purpose, otp):
    """
    Verify an OTP challenge.

    Returns:
        OTPChallenge when verification succeeds.

    Raises:
        ValueError when verification fails.
    """
    email = email.strip().lower()
    otp = otp.strip()

    challenge = (
        OTPChallenge.objects
        .filter(
            email=email,
            purpose=purpose,
            consumed_at__isnull=True,
        )
        .order_by("-created_at")
        .first()
    )

    if challenge is None:
        raise ValueError("No active OTP request found.")

    now = timezone.now()

    if now >= challenge.expires_at:
        raise ValueError("OTP has expired.")

    if challenge.attempts >= challenge.max_attempts:
        raise ValueError("Maximum OTP attempts exceeded.")

    if len(otp) != OTP_LENGTH or not otp.isdigit():
        challenge.attempts += 1
        challenge.save(update_fields=["attempts"])

        raise ValueError("Invalid OTP.")

    if not secrets.compare_digest(
        challenge.code_hash,
        _hash_otp(otp),
    ):
        challenge.attempts += 1
        challenge.save(update_fields=["attempts"])

        if challenge.attempts >= challenge.max_attempts:
            raise ValueError("Maximum OTP attempts exceeded.")

        raise ValueError("Invalid OTP.")

    challenge.consumed_at = now
    challenge.save(update_fields=["consumed_at"])

    return challenge
def request_signup_otp(email, full_name):
    """
    Request an OTP for creating a new account.
    """
    email = email.strip().lower()
    full_name = full_name.strip()

    if not email:
        raise ValueError("Email is required.")

    if not full_name:
        raise ValueError("Full name is required.")

    existing_user = User.objects.filter(email=email).first()

    if existing_user and existing_user.is_verified:
        raise ValueError(
            "An account with this email already exists."
        )

    return request_otp(
        email,
        OTPChallenge.Purpose.SIGNUP,
    )


@transaction.atomic
def verify_signup_otp(email, full_name, otp):
    """
    Verify signup OTP and create/verify the user account.
    """
    email = email.strip().lower()
    full_name = full_name.strip()

    challenge = verify_otp(
        email,
        OTPChallenge.Purpose.SIGNUP,
        otp,
    )

    user = User.objects.filter(email=email).first()

    if user is None:
        user = User.objects.create_user(
            email=email,
            full_name=full_name,
        )

    user.full_name = full_name
    user.is_verified = True
    user.is_active = True

    user.save(
        update_fields=[
            "full_name",
            "is_verified",
            "is_active",
        ]
    )

    return user


def request_login_otp(email):
    """
    Request an OTP for an existing verified user.
    """
    email = email.strip().lower()

    if not email:
        raise ValueError("Email is required.")

    user = User.objects.filter(
        email=email,
        is_verified=True,
        is_active=True,
    ).first()

    if user is None:
        raise ValueError(
            "Your email is not registered. Please sign up first."
        )

    return request_otp(
        email,
        OTPChallenge.Purpose.LOGIN,
    )


def verify_login_otp(email, otp):
    """
    Verify login OTP and return the authenticated user.
    """
    email = email.strip().lower()

    challenge = verify_otp(
        email,
        OTPChallenge.Purpose.LOGIN,
        otp,
    )

    user = User.objects.filter(
        email=email,
        is_verified=True,
        is_active=True,
    ).first()

    if user is None:
        raise ValueError(
            "Unable to complete login."
        )

    return user