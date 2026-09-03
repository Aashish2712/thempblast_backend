from django.db import models
from django.utils.text import slugify
from unidecode import unidecode
from .validators import (
    validate_article_image,
    validate_article_video,
)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(
        max_length=100,
        unique=True,
    )
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    display_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_name = unidecode(self.name)

            base_slug = slugify(
                transliterated_name,
                allow_unicode=False,
            )

            slug = base_slug
            counter = 2

            while Category.objects.filter(
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Article(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="articles",
    )

    headline = models.CharField(max_length=300)

    slug = models.SlugField(
        max_length=320,
        unique=True,
    )

    summary = models.TextField()
    subheadline = models.TextField(blank=True)

    content = models.TextField()

    author = models.CharField(
        max_length=150,
        default="THE MP BLAST रिपोर्टर",
    )

    featured_image = models.ImageField(
        upload_to="articles/featured/",
        blank=True,
        null=True,
        validators=[validate_article_image],
    )
    image_caption = models.CharField(
        max_length=300,
        blank=True,
    )

    district = models.CharField(
        max_length=100,
        blank=True,
    )

    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_breaking = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "-published_at",
            "-created_at",
        ]
        indexes = [
            models.Index(
                fields=["is_published", "-published_at"]
            ),
            models.Index(
                fields=["category", "is_published", "-published_at"]
            ),
        ]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.headline
    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated_headline = unidecode(self.headline)

            base_slug = slugify(
                transliterated_headline,
                allow_unicode=False,
        )

            slug = base_slug
            counter = 2

            while Article.objects.filter(
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

class ArticleContentBlock(models.Model):

    class BlockType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        HEADING = "heading", "Heading"
        QUOTE = "quote", "Quote"

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="content_blocks",
    )

    block_type = models.CharField(
        max_length=20,
        choices=BlockType.choices,
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    text = models.TextField(
        blank=True,
    )

    heading = models.CharField(
        max_length=300,
        blank=True,
    )

    image = models.ImageField(
        upload_to="articles/content/images/",
        blank=True,
        null=True,
        validators=[validate_article_image],
    )

    image_caption = models.CharField(
        max_length=300,
        blank=True,
    )

    image_alt = models.CharField(
        max_length=300,
        blank=True,
    )

    video = models.FileField(
        upload_to="articles/content/videos/",
        blank=True,
        null=True,
        validators=[validate_article_video],
    )

    video_thumbnail = models.ImageField(
        upload_to="articles/content/video-thumbnails/",
        blank=True,
        null=True,
        validators=[validate_article_image],
    )
    video_title = models.CharField(
        max_length=300,
        blank=True,
    )

    video_caption = models.CharField(
        max_length=500,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["display_order", "id"]

        indexes = [
            models.Index(
                fields=["article", "display_order"]
            ),
        ]

        verbose_name = "Article Content Block"
        verbose_name_plural = "Article Content Blocks"

    def __str__(self):
        return (
            f"{self.article.headline} - "
            f"{self.get_block_type_display()} "
            f"#{self.display_order}"
        )
class EditorialPlacement(models.Model):

    class PlacementType(models.TextChoices):
        BREAKING_TICKER = (
            "breaking_ticker",
            "Breaking News Ticker",
            )
        HERO_FEATURED = (
            "hero_featured",
            "Hero Featured",
            )
        LATEST_NEWS = (
            "latest_news",
            "Latest News",
            )

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="editorial_placements",
    )

    placement_type = models.CharField(
        max_length=30,
        choices=PlacementType.choices,
    )

    display_order = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(default=True)

    start_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    end_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "placement_type",
            "display_order",
        ]
        indexes = [
            models.Index(
                fields=[
                    "placement_type",
                    "is_active",
                    "display_order",
                ]
            ),
            models.Index(
                fields=[
                    "placement_type",
                    "start_at",
                    "end_at",
                ]
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "article",
                    "placement_type",
                ],
                name="unique_article_placement_type",
            ),
        ]
        verbose_name = "Editorial Placement"
        verbose_name_plural = "Editorial Placements"

    def __str__(self):
        return (
            f"{self.article.headline} — "
            f"{self.get_placement_type_display()}"
        )