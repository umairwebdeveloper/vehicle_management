from django.contrib import admin
from .models import Thread, Post


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "creator",
        "created_at",
    )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "creator__username")
    list_filter = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "thread",
        "author",
        "share_vehicle",
        "created_at",
    )
    list_filter = (
        "share_vehicle",
        "created_at",
    )
    search_fields = (
        "thread__title",
        "author__username",
        "content",
    )
    raw_id_fields = ("thread", "author", "vehicle")
    date_hierarchy = "created_at"
