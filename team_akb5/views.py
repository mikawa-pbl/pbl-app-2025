from django.shortcuts import render
from django.urls import reverse_lazy
from .models import Member, StatusReport
from .forms import StatusReportForm
from django.views.generic import CreateView, ListView

def index(request):
    return render(request, 'teams/team_akb5/index.html')

def members(request):
    qs = Member.objects.using('team_akb5').all()  # ← team_terrace DBを明示
    return render(request, 'teams/team_akb5/members.html', {'members': qs})


def reports(request):
    qs = StatusReport.objects.using('team_akb5').all()
    return render(request, 'teams/team_akb5/status_report_form.html')

class StatusReportListView(ListView):
    model = StatusReport
    template_name = 'teams/team_akb5/status_list.html' 
    context_object_name = 'reports'
    ordering = ['-created_at'] 

class StatusReportCreateView(CreateView):
    model = StatusReport
    form_class = StatusReportForm 
    template_name = 'teams/team_akb5/status_report_form.html'
    success_url = reverse_lazy('team_akb5:status_list')
