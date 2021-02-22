from django import forms

from .models import Post


class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content"]


class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["id", "content"]
        widgets = {
            "id": forms.HiddenInput
        }
