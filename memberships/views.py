from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .models import Membership

# Create your views here.
def membership_list(request):
    memberships = Membership.objects.all().order_by('price', "name")
    return render(request, 'memberships/membership_list.html', {'memberships': memberships})

class MembershipListView(ListView):
    model = Membership
    template_name = "memberships/membership_list.html"
    context_object_name = "memberships"
    ordering = ["name"]

class MembershipCreateView(CreateView):
    model = Membership
    fields = ["name", "price", "duration_months", "description"]
    template_name = "memberships/membership_form.html"
    success_url = reverse_lazy("membership_list")