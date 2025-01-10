from unicodedata import category
from django import forms
from .models import Post , Category, Comment

# choices=[('coding', 'coding'), ('sports', 'sports'), ('entertainment', 'entertainment'),]
choices = Category.objects.all().values_list('name', 'name')
choice_list=[]
for item in choices:
    choice_list.append(item)

class PostForm (forms.ModelForm):
    class Meta:
        model = Post
        fields =('title', 'author', 'category', 'body', 'snippet', 'header_image')
        widgets ={
            'title':forms.TextInput(attrs={'class' : 'form-control'}),
            # 'author':forms.Select(attrs={'class' : 'form-control'}),
            'author':forms.TextInput(attrs={'class' : 'form-control', 'value':'', 'id':'souha', 'type':'hidden'}),
            'category':forms.Select(choices=choice_list, attrs={'class' : 'form-control'}),
            'body':forms.Textarea(attrs={'class' : 'form-control'}),
            'snippet':forms.Textarea(attrs={'class' : 'form-control'}),
        }

class EditForm (forms.ModelForm):
    class Meta:
        model = Post
        fields =('title',  'body', 'snippet')
        widgets ={
            'title':forms.TextInput(attrs={'class' : 'form-control', 'placeholder':'this is title placeholder stuff'}),
            # 'author':forms.Select(attrs={'class' : 'form-control'}),
            'body':forms.Textarea(attrs={'class' : 'form-control'}),
            'snippet':forms.Textarea(attrs={'class' : 'form-control'}),
        }

class CommentForm (forms.ModelForm):
    class Meta:
        model = Comment
        fields =('name',  'body')
        widgets ={
            'name':forms.TextInput(attrs={'class' : 'form-control'}),
            'body':forms.Textarea(attrs={'class' : 'form-control'}),
            
        }