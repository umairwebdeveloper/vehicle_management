from django.urls import path
from . import views

app_name = "forum"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/new/", views.post_create, name="post_create"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("post/<int:pk>/upvote/", views.upvote_post, name="upvote"),
    path("post/<int:pk>/replies/", views.post_replies, name="post_replies"),
]
