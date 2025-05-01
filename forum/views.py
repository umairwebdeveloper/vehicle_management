from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView
from django.utils import timezone
from .forms import PostForm, ReplyForm
from .models import Post, Reply, Vote, CAT_CHOICES


class PostListView(ListView):
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
        return qs.order_by("-created")


class PostDetailView(DetailView):
    model = Post
    template_name = "forum/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["reply_form"] = ReplyForm()
        return ctx


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(post)
    else:
        form = PostForm()
    return render(request, "forum/post_form.html", {"form": form})


@login_required
def upvote_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    Vote.objects.get_or_create(user=request.user, post=post)
    return redirect("forum:post_list")


@login_required
def post_replies(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.created = timezone.now()
            parent_id = form.cleaned_data.get("parent")
            if parent_id:
                reply.parent_id = parent_id
            reply.save()
            form = ReplyForm() 
    else:
        form = ReplyForm()
    top_replies = post.replies.filter(parent__isnull=True)
    return render(
        request,
        "forum/ajax_replies.html",
        {
            "post": post,
            "reply_form": form,
            "top_replies": top_replies,
        },
    )
