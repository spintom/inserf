from django.shortcuts import render

def home(request):
    from django.contrib.auth.hashers import make_password
    print(make_password("admin123"))

    return render(request, "landing/home.html")
