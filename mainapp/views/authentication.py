from allauth.account.forms import LoginForm, SignupForm
from django.shortcuts import render

def custom_login_view(request):
    context = {
        'login_form': LoginForm(),
    }
    return render(request, 'custom_login_modal.html', context)

def custom_signup_view(request):
    context = {
        'signup_form': SignupForm(),
    }
    return render(request, 'custom_signup_modal.html', context)


