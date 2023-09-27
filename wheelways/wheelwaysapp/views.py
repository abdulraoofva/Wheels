from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib.auth import authenticate, login

from django.http import HttpResponseRedirect
from django.urls import reverse


# Create your views here.
def index(request):
    return render(request,"index.html",)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page or another URL
            return redirect('success_page_name')
        else:
            # Authentication failed, display an error message
            error_message = "Invalid login credentials. Please try again."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        # Display the login form
        return render(request, "login.html")
    
def signup(request):
    return render(request,"signup.html",)
