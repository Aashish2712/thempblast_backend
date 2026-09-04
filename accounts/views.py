import json

from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from .services import (
    request_login_otp,
    request_signup_otp,
    verify_login_otp,
    verify_signup_otp,
)


def _json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON request.")


@require_POST
def signup_request_otp(request):
    try:
        data = _json_body(request)

        email = data.get("email", "")
        full_name = data.get("full_name", "")

        request_signup_otp(email, full_name)

        return JsonResponse({
            "success": True,
            "message": "OTP sent successfully.",
        })

    except ValueError as exc:
        return JsonResponse({
            "success": False,
            "message": str(exc),
        }, status=400)


@require_POST
def signup_verify(request):
    try:
        data = _json_body(request)

        email = data.get("email", "")
        full_name = data.get("full_name", "")
        otp = data.get("otp", "")

        user = verify_signup_otp(
            email,
            full_name,
            otp,
        )

        login(request, user)

        return JsonResponse({
            "success": True,
            "message": "Account created successfully.",
            "user": {
                "email": user.email,
                "full_name": user.full_name,
            },
        })

    except ValueError as exc:
        return JsonResponse({
            "success": False,
            "message": str(exc),
        }, status=400)


# @require_POST
# def login_request_otp(request):
#     try:
#         data = _json_body(request)

#         email = data.get("email", "")

#         request_login_otp(email)

#         return JsonResponse({
#             "success": True,
#             "message": "OTP sent successfully.",
#         })

#     except ValueError:
#         # Don't reveal whether an email belongs to an account.
#         return JsonResponse({
#             "success": True,
#             "message": "If the account is eligible, an OTP has been sent.",
#         })
@require_POST
def login_request_otp(request):
    try:
        data = _json_body(request)
        email = data.get("email", "")

        request_login_otp(email)

        return JsonResponse({
            "success": True,
            "message": "OTP sent successfully.",
        })

    except ValueError as exc:
        return JsonResponse({
            "success": False,
            "message": str(exc),
        }, status=400)


@require_POST
def login_verify(request):
    try:
        data = _json_body(request)

        email = data.get("email", "")
        otp = data.get("otp", "")

        user = verify_login_otp(
            email,
            otp,
        )

        login(request, user)

        return JsonResponse({
            "success": True,
            "message": "Login successful.",
            "user": {
                "email": user.email,
                "full_name": user.full_name,
            },
        })

    except ValueError as exc:
        return JsonResponse({
            "success": False,
            "message": str(exc),
        }, status=400)


@require_POST
def logout_view(request):
    logout(request)

    return JsonResponse({
        "success": True,
        "message": "Logged out successfully.",
    })


@require_GET
def current_user(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "authenticated": False,
        })

    return JsonResponse({
        "authenticated": True,
        "user": {
            "email": request.user.email,
            "full_name": request.user.full_name,
        },
    })
@require_GET
@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({
        "success": True,
        "message": "CSRF cookie set.",
    })
from django.shortcuts import render


def login_page(request):
    return render(request, "thempblast/login.html")