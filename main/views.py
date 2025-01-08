from django.shortcuts import render, redirect
from django.contrib.auth import logout

def index(request):
	return render(request, 'main/index.html')

def logout_view(request):
	logout(request)
	return redirect("main:index")

def pricing(request):
	return render(request, 'main/pricing.html')


def about(request):
	return render(request, 'main/about.html')


def contact(request):
	return render(request, 'main/contact.html')





