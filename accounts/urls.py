from django.urls import path

from . import views


urlpatterns = [
    path("csrf/", views.csrf_token, name="csrf-token"),
    path("signup/request-otp/", views.signup_request_otp, name="signup-request-otp"),
    path("signup/verify/", views.signup_verify, name="signup-verify"),
    path("login/request-otp/", views.login_request_otp, name="login-request-otp"),
    path("login/verify/", views.login_verify, name="login-verify"),
    path("logout/", views.logout_view, name="logout"),
    path("me/", views.current_user, name="current-user"),
    path("login-page/", views.login_page, name="login-page"),
]