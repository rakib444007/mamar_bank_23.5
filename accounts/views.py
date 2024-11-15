from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.views import LoginView,LogoutView,PasswordChangeView
from .forms import UserRegistrationForm,UserUpdateForm,Password_Change_Form
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from django.views import View
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
# from django.contrib.auth.forms import PasswordChangeForm

# Create your views here.


class UserRegistrationView(FormView):
    template_name = 'accounts/user_registration.html'
    form_class = UserRegistrationForm
    success_url= reverse_lazy('profile')


    def form_valid(self, form) :
        user  = form.save()
        login(self.request,user)
        print(user)
        return super().form_valid(form) #form_valid funtion auto call hobe
    
def send_password_change_email(user,  subject, template):
        message = render_to_string(template, {
            'user' : user,
           
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()


class UserLoginView(LoginView):
    template_name ='./accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('homepage')
    

# class UserLogoutView(LogoutView):
#     def get_success_url(self):
#         if self.request.user.is_authenticated:
#             logout(self.request)
#         return reverse_lazy('homepage')

@login_required
def userlogout(request):
    logout(request)
    return redirect('homepage')

# class UserLogoutView(LogoutView):
#     next_page = reverse_lazy('homepage')  # Redirect to the homepage after logout

@method_decorator(login_required,name='dispatch')
class UserBankAccountUpdateView(View):
    template_name = './accounts/profile.html'

    def get(self,request):
        form = UserUpdateForm(instance=request.user)
        return render(request,self.template_name,{'form': form})
    

    def post(self,request):
        form = UserUpdateForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        return render(request,self.template_name,{'form': form})
    

class ChangePasswordView(PasswordChangeView):
    
    form_class = Password_Change_Form
    success_url = reverse_lazy('profile')
    template_name = 'accounts/password_changes.html'
    def form_valid(self,form):
        
        send_password_change_email(self.request.user , 'Password change','accounts/pass_email.html')
        return super().form_valid(form)
