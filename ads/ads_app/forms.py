from django import forms
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

from .models import Ads, Comment


class AdsForm(forms.ModelForm):
    class Meta:
        model = Ads
        fields = [
            'title',
            'text',
            'image',
            'video',
            'category',
        ]
        widgets = {

            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file', 'style': 'width: 50%'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control-file', 'style': 'width: 50%'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        title = cleaned_data.get('title')

        if title == text:
            raise ValidationError(
                "Текст должен отличаться от названия"
            )
        return cleaned_data


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'rows': '4',
    }))

    class Meta:
        model = Comment
        fields = [
            'text',
        ]

