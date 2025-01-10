from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

from django.contrib.auth.models import User 
from django import forms
from blog.models import Profile


# form insta fb bio ..
class ProfilePageForm(forms.ModelForm):
    class Meta:
        model= Profile
        fields=('bio', 'profile_pic', 'website_url', 'twitter_url', 'instagram_url') #, 'pinterest_url'
        widgets={  
            'bio':forms.Textarea(attrs={'class' : 'form-control'}),
            'profile_pic':forms.TextInput(attrs={'class' : 'form-control'}),
            'website_url':forms.TextInput(attrs={'class' : 'form-control'}),
            'twitter_url':forms.TextInput(attrs={'class' : 'form-control'}),
            'instagram_url':forms.TextInput(attrs={'class' : 'form-control'}),
            # 'pinterest_url':forms.TextInput(attrs={'class' : 'form-control'}),
        }

# registration form..
class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control form-control-user "
            }
        ))
    first_name= forms.CharField(max_length=100, widget=forms.TextInput(attrs={ "placeholder": "first name", 'class' : 'form-control form-control-user'}))
    last_name= forms.CharField(max_length=100, widget=forms.TextInput(attrs={"placeholder": "last name", 'class' : 'form-control form-control-user'}))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control form-control-user"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control form-control-user"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control form-control-user"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm , self).__init__( *args, **kwargs)
        self.fields['username'].widget.attrs['class']='form-control form-control-user'
        self.fields['password1'].widget.attrs['class']='form-control form-control-user'
        self.fields['password2'].widget.attrs['class']='form-control form-control-user'


#profile form editing
class EditProfileForm(UserChangeForm):
    email= forms.EmailField(widget=forms.EmailInput(attrs={'class' : 'form-control'}))
    first_name= forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    last_name= forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    username= forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    last_login= forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    last_superuser= forms.CharField(max_length=100, widget=forms.CheckboxInput(attrs={'class' : 'form-check'}))
    is_staff= forms.CharField(max_length=100, widget=forms.CheckboxInput(attrs={'class' : 'form-check'}))
    is_active= forms.CharField(max_length=100, widget=forms.CheckboxInput(attrs={'class' : 'form-check'}))
    date_joined= forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class' : 'form-control'}))
    
    class Meta:
        model =User
        fields =('username', 'first_name', 'last_name', 'email', 'password', 'last_login', 'last_superuser','is_staff', 'is_active', 'date_joined' )

#password changing form
class PasswordChangingForm(PasswordChangeForm):
    old_password= forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'form-control form-control-user', 'type':'password'}))
    new_password1= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class' : 'form-control form-control-user', 'type':'password'}))
    new_password2= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class' : 'form-control form-control-user', 'type':'password'}))

    class Meta:
        model =User
        fields =('old_password', 'new_password1', 'new_password2')
