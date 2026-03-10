from django.urls import path
from .views import member_report, export_members_excel

urlpatterns = [
    path('members/', member_report, name='member_report'),
    path('members/export/', export_members_excel, name='export_members_excel'),
]