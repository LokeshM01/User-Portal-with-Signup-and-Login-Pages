from django.shortcuts import render

from django.http import HttpResponse

def home_view(request):
    return HttpResponse('<h2>Welcome to the Home Page</h2>')

# Create your views here.
