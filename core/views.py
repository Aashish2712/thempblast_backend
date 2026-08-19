from django.shortcuts import render


def home(request):
    return render(request, "thempblast/index.html")


def article(request):
    return render(request, "thempblast/article.html")

def category(request):
    return render(request, "thempblast/category.html")


def about(request):
    return render(request, "thempblast/about.html")


def contact(request):
    return render(request, "thempblast/contact.html")

def login(request):
    return render(request, "thempblast/login.html")