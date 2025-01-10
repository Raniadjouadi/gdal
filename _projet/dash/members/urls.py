from django.urls import path
from .views import UserRegistrationView, UserEditView, PasswordsChangeView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'members'

urlpatterns = [
    path('register/', UserRegistrationView, name='register'),
    path('edit_profile/', UserEditView.as_view(), name='edit_profile'),
    # path('password/', auth_views.PasswordChangeView.as_view(template_name='registration/change-password.html')),
    path('password/', PasswordsChangeView.as_view(template_name='registration/change-password.html'),name='change_password'),
    path('password_success',views.password_success, name="password_success" ),
    path("reset_password",auth_views.PasswordResetView.as_view(), name="forgot_password"),  #submit email form
    path("reset_password_sent",auth_views.PasswordResetDoneView.as_view(), name="reset_password_sent"), #email sent success message
    path("reset/<uidb64>/<token>",auth_views.PasswordResetConfirmView.as_view(), name="reset_password_confirm"), #link to passsword rest form in email
    path("reset_password_complete",auth_views.PasswordResetCompleteView.as_view(), name="reset_password_complete"), #password successfully changed message

    #path('<int:pk>/profile/',ShowProfilePageView.as_view(), name="show_pofile_page" ),
    # path('<int:pk>/edit_profile_page/',EditProfilePageView.as_view(), name="edit_pofile_page" ),
    # path('create_profile_page/',CreateProfilePageView.as_view(), name="create_pofile_page" ),
]

