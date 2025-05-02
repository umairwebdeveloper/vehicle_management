from django import forms
from .models import Post, Reply
from vehicles.models import Vehicle


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["vehicle", "cat", "title", "body", "share_vehicle", "solved"]
        widgets = {
            "vehicle": forms.Select(attrs={"class": "form-select"}),
            "cat": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "share_vehicle": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "solved": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        help_texts = {
            "vehicle": "Optional: choose a vehicle to associate with this post.",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(owner=user)
        else:
            self.fields["vehicle"].queryset = Vehicle.objects.none()

    def clean(self):
        cleaned = super().clean()
        share = cleaned.get("share_vehicle")
        vehicle = cleaned.get("vehicle")
        if share and not vehicle:
            self.add_error(
                "vehicle",
                "You must select a vehicle if you choose to share vehicle details.",
            )
        return cleaned


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ["post", "parent", "body"]
        widgets = {
            "post": forms.HiddenInput(),
            "parent": forms.HiddenInput(),
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write your reply…",
                }
            ),
        }
