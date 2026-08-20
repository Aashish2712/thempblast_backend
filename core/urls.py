from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("article/", views.article, name="article"),
    path("category/", views.category, name="category"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login, name="login"),
    path(
    "api/contact/",
    views.contact_submit,
    name="contact_submit",
),
]