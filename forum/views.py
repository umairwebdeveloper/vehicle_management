from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Exists, OuterRef, Value, BooleanField
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.utils import timezone
from .forms import PostForm, ReplyForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Reply, Vote, CAT_CHOICES
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string


class PostListView(ListView):
    login_url = "/auth/login/"
    model = Post
    paginate_by = 20
    template_name = "forum/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))
        cat = self.request.GET.get("category")
        if cat:
            qs = qs.filter(cat=cat)

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_liked=Exists(
                    Vote.objects.filter(
                        post=OuterRef("pk"), user=self.request.user, value=1
                    )
                )
            )
        else:
            qs = qs.annotate(is_liked=Value(False, output_field=BooleanField()))

        return qs.order_by("-created")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = CAT_CHOICES
        ctx["current_category"] = self.request.GET.get("category", "")
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class MyPostsListView(LoginRequiredMixin, ListView):
    login_url = "/auth/login/"
    model = Post
    paginate_by = 20
    template_name = "forum/my_post_list.html"  
    context_object_name = "posts"

    def get_queryset(self):
        qs = super().get_queryset().filter(author=self.request.user)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))
        cat = self.request.GET.get("category")
        if cat:
            qs = qs.filter(cat=cat)

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_liked=Exists(
                    Vote.objects.filter(
                        post=OuterRef("pk"), user=self.request.user, value=1
                    )
                )
            )
        else:
            qs = qs.annotate(is_liked=Value(False, output_field=BooleanField()))

        return qs.order_by("-created")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = CAT_CHOICES
        ctx["current_category"] = self.request.GET.get("category", "")
        ctx["query"] = self.request.GET.get("q", "")
        ctx["view_title"] = "My Posts"  # new!
        return ctx


class PostCreateView(LoginRequiredMixin, CreateView):
    login_url = "/auth/login/"
    model = Post
    form_class = PostForm
    template_name = "forum/post_form.html"
    success_url = reverse_lazy("forum:post_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "/auth/login/"
    model = Post
    form_class = PostForm
    template_name = "forum/post_form.html"
    success_url = reverse_lazy("forum:post_list")

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


@login_required
def upvote_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    vote, created = Vote.objects.get_or_create(user=request.user, post=post)
    if not created:
        vote.delete()
    return redirect("forum:post_list")


@require_http_methods(["GET"])
def post_replies(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = ReplyForm(initial={"post": post.pk})
    replies = (
        post.replies.filter(parent__isnull=True)
        .select_related("author")
        .prefetch_related("children__author")
    )
    html = render_to_string(
        "forum/_replies_modal.html",
        {"post": post, "form": form, "replies": replies},
        request=request,
    )
    return JsonResponse({"html": html})


@login_required
@require_http_methods(["POST"])
def reply_create(request):
    reply_pk = request.POST.get("reply_pk")
    if reply_pk:
        reply = get_object_or_404(Reply, pk=reply_pk, author=request.user)
        original_parent = reply.parent
        form = ReplyForm(request.POST, instance=reply)
    else:
        form = ReplyForm(request.POST)

    if form.is_valid():
        reply = form.save(commit=False)
        reply.author = request.user
        # preserve parent on edit
        if reply_pk:
            reply.parent = original_parent
        reply.save()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@login_required
@require_http_methods(["POST"])
def reply_delete(request, pk):
    reply = get_object_or_404(Reply, pk=pk, author=request.user)
    reply.delete()
    return JsonResponse({"success": True})
