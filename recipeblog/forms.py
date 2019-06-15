from django import forms
from recipeblog.models import Post, Comment


class PostForm(forms.ModelForm):
    # model form inline meta class
    class Meta():
        # connect models we use
        model = Post
        fields = ('title', 'image', 'description', 'difficulty', 'ingredient')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'textinputclass'}),
            'description': forms.Textarea(attrs={'class': 'editable medium-editor-textarea postcontent'}),
        }

class CommentForm(forms.ModelForm):

    class Meta():
        model = Comment
        fields = ('author', 'text')

        widgets = {
            'author': forms.TextInput(attrs={'class': 'textinputclass'}),
            'text': forms.Textarea(attrs={'class': 'editable medium-editor-textarea'})
        }

