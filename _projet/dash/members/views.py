from cProfile import Profile
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.views.generic import DetailView, CreateView
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import SignUpForm, EditProfileForm, PasswordChangingForm, ProfilePageForm
from blog.models import Profile
from django.contrib import messages
from django.contrib.auth import authenticate, login , logout



# views insta fb bio ..
# class CreateProfilePageView(CreateView):
#     model=Profile
#     form_class=ProfilePageForm
#     template_name = 'registration/create_user_profile_page.html'
#     # fields= '__all__'
#     def form_valid(self, form):
#         form.instance.user=self.request.user
#         return super().form_valid(form)



# views password changing form 
class PasswordsChangeView(PasswordChangeView):
    form_class=PasswordChangingForm
    success_url = reverse_lazy ('members:password_success')


# password success rendering page ..
def password_success(request):
    return render(request, 'registration/password_success.html', {})


# registration page ..
# class UserRegistrationView(generic.CreateView):
#     form_class = SignUpForm
#     template_name = 'registration/register.html'
#     success_url = reverse_lazy ('login')


def UserRegistrationView(request):
        form =  SignUpForm
        if request.method == 'POST':
          form =  SignUpForm(request.POST)
          if form.is_valid():
             form.save()
             user = form.cleaned_data.get('username') 
             messages.success(request,'Account created succefully for '+ user)
             return redirect('login')
       
        context = {'form' : form}
        return render (request,'registration/register.html', context )
        

# edit profile page ..
class UserEditView(generic.UpdateView):
    form_class = EditProfileForm
    # fields ='__all__'
    template_name = 'registration/edit_profile.html'
    success_url = reverse_lazy ('blog:home')

    def get_object(self):
        return self.request.user

