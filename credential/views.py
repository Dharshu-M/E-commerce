from django.shortcuts import render, redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages

# Create your views here.

def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'An account with that email already exists.')
        else:
            user=User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )
            messages.success(request, 'Your account has been created.')
            user.save()
            return redirect('register')

    return render(request, 'credential/register.html')

def login(request):
    if request.method == "POST":
        username=request.POST["username"]
        password=request.POST["password"]
        
        user=auth.authenticate(username=username,password=password)
        
        if user is not None: 
            auth.login(request,user)
            return redirect("/")
        else:
            messages.info(request,"invalid credential")
    else:
        return render(request,'credential/login.html')