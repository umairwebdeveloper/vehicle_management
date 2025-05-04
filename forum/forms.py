from django import forms
from .models import Post, Reply
from vehicles.models import Vehicle
from django.forms import ClearableFileInput


class MultiFileClearableInput(ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiFileClearableInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data and initial:
            return initial

        if isinstance(data, (list, tuple)):
            return [super(MultipleFileField, self).clean(file) for file in data]
        return super(MultipleFileField, self).clean(data)


class PostForm(forms.ModelForm):
    images = MultipleFileField(
        required=False,
        help_text="Select up to 5 images to upload (max 5MB each).",
        widget=MultiFileClearableInput(
            attrs={"class": "form-control", "accept": "image/*", "multiple": True}
        ),
    )

    class Meta:
        model = Post
        fields = [
            "vehicle",
            "cat",
            "title",
            "body",
            "share_vehicle",
            "solved",
            "sold",
        ]
        widgets = {
            "vehicle": forms.Select(attrs={"class": "form-select"}),
            "cat": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "share_vehicle": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "solved": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "sold": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        help_texts = {
            "vehicle": "Optional: choose a vehicle to associate with this post.",
        }

    def clean_images(self):
        images = self.cleaned_data.get("images", [])

        if not images:
            return images

        if self.instance and self.instance.pk:
            existing_count = self.instance.images.count()
        else:
            existing_count = 0

        if len(images) + existing_count > 5:
            raise forms.ValidationError(
                "You can upload a maximum of 5 images per post."
            )

        for image in images:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    f"Image '{image.name}' is too large (max 5MB each)."
                )
            if not image.content_type.startswith("image/"):
                raise forms.ValidationError("Only image files are allowed.")

        return images

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
