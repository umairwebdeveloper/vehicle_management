from django.db import models
from django.utils.text import slugify
from vehicles.models import Vehicle
from django.contrib.auth.models import User

class Thread(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220, unique=True, blank=True, help_text="Auto-generated from title."
    )
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="threads")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Thread"
        verbose_name_plural = "Threads"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            self.slug = base
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    share_vehicle = models.BooleanField(
        default=False, help_text="Include your vehicle summary with this post."
    )
    vehicle = models.ForeignKey(
        Vehicle,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Vehicle to show if sharing is enabled.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["created_at"]

    def clean(self):
        if self.share_vehicle and not self.vehicle:
            from django.core.exceptions import ValidationError

            raise ValidationError("Select a vehicle to share.")

    def __str__(self):
        return f"Post by {self.author} on {self.thread.title}"
