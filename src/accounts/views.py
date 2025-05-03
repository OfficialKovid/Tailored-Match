from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = User.objects.filter(username = username)
        if user.exists():
            messages.info(request,'Username already exist')
            return redirect('/signup/')

        user = User.objects.create(
            email=email,
            username=username
        )
        user.set_password(password)
        user.save()
        return redirect('/login/')
    return render(request, "accounts/signup.html")  # Updated template path

def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not User.objects.filter(username = username).exists():
            messages.info(request,'Wrong Username')
            return redirect('/login/')
            
        user = authenticate(username = username, password = password)
        if user is None:
            messages.error(request,'Wrong Passward')
            return redirect('/login/')
        else:
            login(request,user)
            return redirect('/')

    return render(request, "accounts/login.html") 

@login_required(login_url='/login/')
def account(request):
    return render(request,"account.html")

@login_required(login_url='/account/')
def orders(request):
    return render(request,"orders.html")

def logout_user(request):
    logout(request)
    return redirect('/login/')