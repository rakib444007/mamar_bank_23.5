
from django.urls import path
from .views import UserRegistrationView,UserLoginView,userlogout,UserBankAccountUpdateView,ChangePasswordView
urlpatterns = [
    path('register/',UserRegistrationView.as_view(),name='register'),
    path('login/',UserLoginView.as_view(),name='user_login'),
    path('logout/',userlogout,name='user_logout'),
    path('profile/',UserBankAccountUpdateView.as_view(),name='profile'),
    path('pass_changes',ChangePasswordView.as_view(),name='pass_change'),

    
]

