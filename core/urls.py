from django.urls import path
from . import views


urlpatterns = [
    
    # Website pages
    path("", views.home, name="home"),
    path(
        "article/<slug:slug>/",
        views.article,
        name="article",
    ),
    path("category/", views.category, name="category"),
    path(
        "category/<slug:slug>/",
        views.category,
        name="category_detail_page"),
        
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login, name="login"),

    # Contact API
    path(
        "api/contact/",
        views.contact_submit,
        name="contact_submit",
    ),

    # Home editorial APIs
    path(
    "api/home/",
    views.home_data,
    name="home_data",
),
    path(
        "api/home/breaking/",
        views.home_breaking,
        name="home_breaking",
    ),
    path(
        "api/home/hero/",
        views.home_hero,
        name="home_hero",
    ),
    path(
        "api/home/latest/",
        views.home_latest,
        name="home_latest",
    ),

    # Category APIs
    path(
        "api/categories/",
        views.category_list,
        name="category_list",
    ),
    path(
        "api/categories/<slug:slug>/",
        views.category_detail,
        name="category_detail",
    ),

    # Article APIs
    path(
        "api/articles/",
        views.article_list,
        name="article_list",
    ),
    path(
        "api/articles/<slug:slug>/",
        views.article_detail,
        name="article_detail"),

    # Articles belonging to a category
    path(
        "api/categories/<slug:slug>/articles/",
        views.category_articles,
        name="category_articles",
    ),
]