from django import forms
from .models import Post, Reply


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["cat", "title", "body", "share_vehicle"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 5}),
        }


class ReplyForm(forms.ModelForm):
    parent = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Reply
        fields = ["body", "parent"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3}),
        }
