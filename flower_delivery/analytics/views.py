from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import DailyReport

@staff_member_required
def daily_report_list(request):
    reports = DailyReport.objects.all()
    return render(request, 'analytics/daily_report_list.html', {'reports': reports})
