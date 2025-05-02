from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from vehicles.models import Vehicle

CAT_CHOICES = [
    ("maintenance", "Maintenance Help"),
    ("diy", "DIY Repairs"),
    ("buying", "Buying/Selling Advice"),
    ("general", "General Discussion"),
]


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="vehicle_post",
        help_text="Vehicle related to this post",
    )
    cat = models.CharField(max_length=100, choices=CAT_CHOICES, default="general")
    title = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    solved = models.BooleanField(default=False)
    share_vehicle = models.BooleanField(
        default=False,
        help_text="Share my vehicle details on this post",
    )

    def __str__(self):
        return self.title

    def reply_count(self):
        return self.replies.count()

    def upvote_count(self):
        return self.votes.filter(value=1).count()


class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="replies")
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        help_text="Reply to another reply",
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    is_solution = models.BooleanField(default=False)

    def __str__(self):
        return f"Reply by {self.author} on {self.post}"


class Vote(models.Model):
    """Upvote only (you could extend to downvotes if you like)"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="votes")
    value = models.SmallIntegerField(default=1)  # always +1 here

    class Meta:
        unique_together = ("user", "post")
