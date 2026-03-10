from django.shortcuts import render
from memberships.models import Member
from django.http import HttpResponse
import openpyxl
from django.template.loader import get_template


def member_report(request):

    status = request.GET.get('status')

    if status == "active":
        members = Member.objects.filter(status=True)

    elif status == "inactive":
        members = Member.objects.filter(status=False)

    else:
        members = Member.objects.all()

    # estadísticas
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status=True).count()
    inactive_members = Member.objects.filter(status=False).count()

    context = {
        "members": members,
        "status_filter": status,
        "total_members": total_members,
        "active_members": active_members,
        "inactive_members": inactive_members
    }

    return render(request, "reports/member_report.html", context)


def export_members_excel(request):
    
    status = request.GET.get('status')
    if status == "active":
        members = Member.objects.filter(status=True)
    elif status == "inactive":
        members = Member.objects.filter(status=False)
    else:
        members = Member.objects.all()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Miembros"

    # encabezados
    sheet.append(["Nombre", "Documento", "Email", "Membresía", "Estado"])

    # datos
    for member in members:
        sheet.append([
            member.full_name,
            member.document,
            member.email,
            member.membership.name,
            member.status
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = 'attachment; filename="members_report.xlsx"'

    workbook.save(response)

    return response
