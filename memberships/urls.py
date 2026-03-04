from django.urls import path
from .views import (
    LandingPageView, 
    MembershipListView, 
    MembershipCreateView,
    MembershipUpdateView,
    MembershipDeleteView,
    AdminUserCreateView,
    AdminUserListView,
    AdminUserDeleteView,
    MemberRegisterView,
    MemberRegisterSuccessView,
    MemberListView,
    MemberCreateView,
    MemberUpdateView,
    MemberDeleteView,
)

urlpatterns = [
    path("", LandingPageView.as_view(), name="landing"),
    
    # Membership URLs (Admin Only)
    path("memberships/", MembershipListView.as_view(), name="membership_list"),
    path("memberships/create/", MembershipCreateView.as_view(), name="membership_create"),
    path("memberships/<int:pk>/edit/", MembershipUpdateView.as_view(), name="membership_edit"),
    path("memberships/<int:pk>/delete/", MembershipDeleteView.as_view(), name="membership_delete"),
    
    # Member URLs
    path("register/", MemberRegisterView.as_view(), name="member_register"),
    path("register/success/", MemberRegisterSuccessView.as_view(), name="member_register_success"),
    path("members/", MemberListView.as_view(), name="member_list"),
    path("members/create/", MemberCreateView.as_view(), name="member_create"),
    path("members/<int:pk>/edit/", MemberUpdateView.as_view(), name="member_edit"),
    path("members/<int:pk>/delete/", MemberDeleteView.as_view(), name="member_delete"),
    
    # Admin Users URLs
    path("administration/create-admin/", AdminUserCreateView.as_view(), name="admin_user_create"),
    path("administration/admins/", AdminUserListView.as_view(), name="admin_user_list"),
    path("administration/admins/<int:pk>/delete/", AdminUserDeleteView.as_view(), name="admin_user_delete"),
]