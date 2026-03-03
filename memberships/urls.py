from django.urls import path
from .views import MembershipListView, MembershipCreateView

urlpatterns = [
    path("", MembershipListView.as_view(), name="membership_list"),
    path("create/", MembershipCreateView.as_view(), name="membership_create"),
]