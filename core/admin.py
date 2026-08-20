from django.contrib import admin

from .models import (
    Article,
    ArticleContentBlock,
    Category,
    EditorialPlacement,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "display_order",
        "is_active",
        "is_archived",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "is_archived",
    )

    search_fields = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    ordering = (
        "display_order",
        "name",
    )

class ArticleContentBlockInline(admin.StackedInline):
    model = ArticleContentBlock

    extra = 1

    fields = (
        "block_type",
        "display_order",
        "text",
        "heading",
        "image",
        "image_caption",
        "image_alt",
        "video",
        "video_thumbnail",
        "video_title",
        "video_caption",
    )

    ordering = (
        "display_order",
        "id",
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = (
        ArticleContentBlockInline,
    )
    list_display = (
        "headline",
        "category",
        "district",
        "is_published",
        "is_breaking",
        "is_featured",
        "published_at",
        "views",
        "updated_at",
    )

    list_filter = (
        "category",
        "is_published",
        "is_breaking",
        "is_featured",
    )

    search_fields = (
        "headline",
        "summary",
        "subheadline",
        "content",
        "author",
        "district",
    )

    prepopulated_fields = {
        "slug": ("headline",),
    }

    autocomplete_fields = (
        "category",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "published_at"

    ordering = (
        "-published_at",
        "-created_at",
    )

@admin.register(ArticleContentBlock)
class ArticleContentBlockAdmin(admin.ModelAdmin):

    list_display = (
        "article",
        "block_type",
        "display_order",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "block_type",
    )

    search_fields = (
        "article__headline",
        "text",
        "heading",
        "image_caption",
        "video_title",
    )

    autocomplete_fields = (
        "article",
    )

    ordering = (
        "article",
        "display_order",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
@admin.register(EditorialPlacement)
class EditorialPlacementAdmin(admin.ModelAdmin):
    list_display = (
        "article",
        "placement_type",
        "display_order",
        "is_active",
        "start_at",
        "end_at",
    )

    list_filter = (
        "placement_type",
        "is_active",
    )

    search_fields = (
        "article__headline",
    )

    autocomplete_fields = (
        "article",
    )

    ordering = (
        "placement_type",
        "display_order",
    )