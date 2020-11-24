from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['comment'].label = False

    comment = forms.CharField(
        min_length=2, max_length=256, 
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter your comment here',
            'rows': '2',
            'cols': '60',
        }))

    class Meta:
        model = Comment
        fields = ['comment']
