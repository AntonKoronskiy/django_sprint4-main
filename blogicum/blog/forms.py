from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'datetime-local'})
        }


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class RegistrationForm(UserCreationForm):
    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name')
        model = User


class EditProfileForm(forms.ModelForm):
    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name')
        model = User
