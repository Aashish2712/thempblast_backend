from pathlib import Path

from django.shortcuts import render
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from .models import (
    Article,
    Category,
    EditorialPlacement,
)


def home(request):
    return render(request, "thempblast/index.html")


def article(request, slug):
    return render(
        request,
        "thempblast/article.html",
        {
            "article_slug": slug,
        },
    )

def category(request):
    return render(request, "thempblast/category.html")


def about(request):
    return render(request, "thempblast/about.html")


def contact(request):
    return render(request, "thempblast/contact.html")

def login(request):
    return render(request, "thempblast/login.html")
@require_POST
def contact_submit(request):
    """
    V1 Contact submission.

    - Requires authenticated session.
    - Does not save anything in the database.
    - Does not permanently store uploaded files.
    - Sends the message and optional attachments by email.
    """

    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "success": False,
                "message": "Login required.",
            },
            status=401,
        )

    name = (request.POST.get("name") or "").strip()
    subject = (request.POST.get("subject") or "").strip()
    message = (request.POST.get("message") or "").strip()

    # ---------------------------------------------------------
    # Basic field validation
    # ---------------------------------------------------------

    if len(name) < 2:
        return JsonResponse(
            {
                "success": False,
                "message": "Please enter a valid name.",
            },
            status=400,
        )

    if len(subject) < 3:
        return JsonResponse(
            {
                "success": False,
                "message": "Please enter a valid subject.",
            },
            status=400,
        )

    if len(message) < 10:
        return JsonResponse(
            {
                "success": False,
                "message": "Message must be at least 10 characters.",
            },
            status=400,
        )

    # ---------------------------------------------------------
    # Authenticated identity
    # ---------------------------------------------------------

    user_email = request.user.email

    recipient = getattr(
        settings,
        "CONTACT_RECIPIENT_EMAIL",
        None,
    )

    if not recipient:
        return JsonResponse(
            {
                "success": False,
                "message": "Contact email is not configured.",
            },
            status=500,
        )

    # ---------------------------------------------------------
    # Attachment rules
    # ---------------------------------------------------------

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".pdf",
        ".mp4",
        ".mov",
    }

    max_files = 5
    max_single_size = 10 * 1024 * 1024       # 10 MB
    max_total_size = 20 * 1024 * 1024        # 20 MB

    attachments = request.FILES.getlist("attachments")

    if len(attachments) > max_files:
        return JsonResponse(
            {
                "success": False,
                "message": f"You can attach a maximum of {max_files} files.",
            },
            status=400,
        )

    total_size = 0

    for uploaded_file in attachments:
        filename = Path(uploaded_file.name).name
        suffix = Path(filename).suffix.lower()

        if suffix not in allowed_extensions:
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        f"File type '{suffix or 'unknown'}' "
                        "is not allowed."
                    ),
                },
                status=400,
            )

        if uploaded_file.size > max_single_size:
            return JsonResponse(
                {
                    "success": False,
                    "message": (
                        f"'{filename}' is larger than "
                        "the 10 MB single-file limit."
                    ),
                },
                status=400,
            )

        total_size += uploaded_file.size

    if total_size > max_total_size:
        return JsonResponse(
            {
                "success": False,
                "message": "Total attachment size cannot exceed 20 MB.",
            },
            status=400,
        )

    # ---------------------------------------------------------
    # Build email
    # ---------------------------------------------------------

    email_subject = f"[THE MP BLAST Contact] {subject}"

    email_body = (
        "New contact message received.\n\n"
        f"Name: {name}\n"
        f"Email: {user_email}\n"
        f"Subject: {subject}\n"
        f"Attachments: {len(attachments)}\n\n"
        "Message:\n"
        f"{message}\n"
    )

    try:
        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            reply_to=[user_email],
        )

        # -----------------------------------------------------
        # Add attachments directly to the email
        # -----------------------------------------------------

        for uploaded_file in attachments:
            email.attach(
                uploaded_file.name,
                uploaded_file.read(),
                uploaded_file.content_type,
            )

        email.send(fail_silently=False)

    except Exception:
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Unable to send your message right now. "
                    "Please try again."
                ),
            },
            status=500,
        )

    return JsonResponse(
        {
            "success": True,
            "message": "Your message was sent successfully.",
            "attachments_sent": len(attachments),
        }
    )
def get_editorial_articles(placement_type):
    now = timezone.now()

    return (
        EditorialPlacement.objects
        .select_related(
            "article",
            "article__category",
        )
        .filter(
            placement_type=placement_type,
            is_active=True,
            article__is_published=True,
        )
        .filter(
            models.Q(start_at__isnull=True)
            | models.Q(start_at__lte=now)
        )
        .filter(
            models.Q(end_at__isnull=True)
            | models.Q(end_at__gte=now)
        )
        .order_by("display_order")
    )
def serialize_content_block(block):
    data = {
        "type": block.block_type,
        "order": block.display_order,
    }

    if block.block_type == "text":
        data["text"] = block.text

    elif block.block_type == "heading":
        data["heading"] = block.heading

    elif block.block_type == "quote":
        data["text"] = block.text

    elif block.block_type == "image":
        data["image"] = (
            block.image.url
            if block.image
            else ""
        )

        data["caption"] = block.image_caption
        data["alt"] = block.image_alt

    elif block.block_type == "video":
        data["video"] = (
            block.video.url
            if block.video
            else ""
        )

        data["thumbnail"] = (
            block.video_thumbnail.url
            if block.video_thumbnail
            else ""
        )

        data["title"] = block.video_title
        data["caption"] = block.video_caption

    return data
def serialize_article(article):
    content_blocks = (
        article.content_blocks
        .all()
        .order_by("display_order", "id")
    )

    return {
        "id": article.id,
        "headline": article.headline,
        "summary": article.summary,
        "subheadline": article.subheadline,
        "slug": article.slug,

        "image": (
            article.featured_image.url
            if article.featured_image
            else ""
        ),

        "imageCaption": article.image_caption,

        "category": article.category.slug,
        "catLabel": article.category.name,

        "district": article.district,
        "author": article.author,

        "isBreaking": article.is_breaking,
        "isFeatured": article.is_featured,

        "views": article.views,

        "publishedAt": (
            article.published_at.isoformat()
            if article.published_at
            else None
        ),

        "updatedAt": (
            article.updated_at.isoformat()
            if article.updated_at
            else None
        ),

        "content": article.content,

        "contentBlocks": [
            serialize_content_block(block)
            for block in content_blocks
        ],
    }


def home_breaking(request):
    placements = get_editorial_articles(
        EditorialPlacement.PlacementType.BREAKING_TICKER
    )

    return JsonResponse({
        "success": True,
        "items": [
            serialize_article(placement.article)
            for placement in placements
        ],
    })
def home_hero(request):
    placements = get_editorial_articles(
        EditorialPlacement.PlacementType.HERO_FEATURED
    )

    return JsonResponse({
        "success": True,
        "items": [
            serialize_article(placement.article)
            for placement in placements
        ],
    })
def home_latest(request):
    placements = get_editorial_articles(
        EditorialPlacement.PlacementType.LATEST_NEWS
    )

    return JsonResponse({
        "success": True,
        "items": [
            serialize_article(placement.article)
            for placement in placements
        ],
    })
def serialize_category(category):
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "displayOrder": category.display_order,
    }
def category_list(request):
    categories = (
        Category.objects
        .filter(
            is_active=True,
            is_archived=False,
        )
        .order_by("display_order", "name")
    )

    return JsonResponse({
        "success": True,
        "items": [
            serialize_category(category)
            for category in categories
        ],
    })
def category_detail(request, slug):
    try:
        category = (
            Category.objects
            .filter(
                is_active=True,
                is_archived=False,
                slug=slug,
            )
            .get()
        )
    except Category.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Category not found.",
            },
            status=404,
        )

    return JsonResponse({
        "success": True,
        "item": serialize_category(category),
    })
def article_list(request):
    articles = (
        Article.objects
        .select_related("category")
        .prefetch_related("content_blocks")
        .filter(
            is_published=True,
            category__is_active=True,
            category__is_archived=False,
        )
        .order_by("-published_at", "-created_at")
    )

    return JsonResponse({
        "success": True,
        "items": [
            serialize_article(article)
            for article in articles
        ],
    })
def article_detail(request, slug):
    try:
        article = (
            Article.objects
            .select_related("category")
            .prefetch_related("content_blocks")
            .get(
                slug=slug,
                is_published=True,
                category__is_active=True,
                category__is_archived=False,
            )
        )
    except Article.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Article not found.",
            },
            status=404,
        )

    return JsonResponse({
        "success": True,
        "item": serialize_article(article),
    })
def category_articles(request, slug):
    try:
        category = (
            Category.objects
            .get(
                slug=slug,
                is_active=True,
                is_archived=False,
            )
        )
    except Category.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "message": "Category not found.",
            },
            status=404,
        )

    articles = (
        Article.objects
        .select_related("category")
        .prefetch_related("content_blocks")
        .filter(
            category=category,
            is_published=True,
        )
        .order_by("-published_at", "-created_at")
    )

    return JsonResponse({
        "success": True,
        "category": serialize_category(category),
        "items": [
            serialize_article(article)
            for article in articles
        ],
    })