from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def membership_list(request):
    return render(request, 'memberships/membership_list.html')
