from typing import Any
from django import forms
from .models import Post, Story
from django.contrib.auth import get_user_model

User = get_user_model()



class PostForm(forms.ModelForm):

    user=None

    class Meta:
        model = Post
        fields = [
                  'file',
                  'caption',
                  'hash_tag',
                  'mentions',
                  'location',
                  'private'
                  ]

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)
        if user_id:
            self.user = User.objects.get(id=user_id)
           
    def clean(self):
        cleaned_data = super(PostForm, self).clean()
        hash_tag = cleaned_data.get('hash_tag')

        if hash_tag and len(hash_tag) > 3:
            raise forms.ValidationError('You can only use up to 3 hash tags.')
        return cleaned_data

    def save(self, commit=True) -> Any:
        post = super().save(commit=False)
        post.user = self.user
        if commit:
            post.save()
        return post
    

class StoryForm(forms.ModelForm):
    user=None

    class Meta:
        model = Story
        fields = [
                  'file',
                  'caption',
                  'hash_tag',
                  'mentions',
                  'location',
                  ]

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)
        if user_id:
            self.user = User.objects.get(id=user_id)
           
    def clean(self):
        cleaned_data = super(StoryForm, self).clean()
        hash_tag = cleaned_data.get('hash_tag')

        if hash_tag and len(hash_tag) > 3:
            raise forms.ValidationError('You can only use up to 3 hash tags.')
        return cleaned_data

    def save(self, commit=True) -> Any:
        post = super().save(commit=False)
        post.user = self.user
        if commit:
            post.save()
        return post