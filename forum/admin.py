from django.contrib import admin
from .models import Post, Reply, Vote, PostImage


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "cat", "created", "solved", "share_vehicle")
    list_filter = ("cat", "solved")
    search_fields = ("title", "body", "author__username")
    date_hierarchy = "created"
    raw_id_fields = ("author",)
    actions = ["mark_as_solved", "unmark_as_solved"]

    def mark_as_solved(self, request, queryset):
        queryset.update(solved=True)

    mark_as_solved.short_description = "Mark selected posts as solved"

    def unmark_as_solved(self, request, queryset):
        queryset.update(solved=False)

    unmark_as_solved.short_description = "Unmark selected posts as solved"

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ("post", "image")
    search_fields = ("post__title",)
    raw_id_fields = ("post",)
    list_filter = ("post__cat",)

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created", "is_solution")
    list_filter = ("is_solution",)
    search_fields = ("body", "author__username")
    date_hierarchy = "created"


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "value")
    search_fields = ("user__username", "post__title")
