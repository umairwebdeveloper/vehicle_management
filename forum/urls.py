from django.urls import path
from . import views

app_name = "forum"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("my/", views.MyPostsListView.as_view(), name="my_post"),
    path("post/new/", views.PostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post-edit"),
    path("post/<int:pk>/upvote/", views.upvote_post, name="upvote"),
    path("post/<int:pk>/replies/", views.post_replies, name="post-replies"),
    path("reply/create/", views.reply_create, name="reply-create"),
    path("reply/<int:pk>/delete/", views.reply_delete, name="reply-delete"),
]
