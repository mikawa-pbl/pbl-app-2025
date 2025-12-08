from django.shortcuts import render, redirect
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

class AdminView(ListView):
    model = StatusReport
    template_name = 'teams/team_akb5/admin.html' 
    context_object_name = 'reports'
    ordering = ['-created_at'] 

    def post(self, request, *args, **kwargs):
        report_id = request.POST.get('report_id')
        if report_id:
            report = StatusReport.objects.using('team_akb5').get(id=report_id)
            report.delete()
        return redirect('team_akb5:admin')

class StatusReportCreateView(CreateView):
    model = StatusReport
    form_class = StatusReportForm 
    template_name = 'teams/team_akb5/status_report_form.html'
    success_url = reverse_lazy('team_akb5:admin')

from django.utils import timezone # 追加: 日時処理用
from datetime import timedelta    # 追加: 時間差計算用

# ... (中略: 他のView関数などはそのまま) ...

class UserView(ListView):
    model = StatusReport
    template_name = 'teams/team_akb5/user.html' 
    context_object_name = 'reports'
    
    def get_queryset(self):
        """
        直近30秒以内に作成されたレポートのみを返す
        """
        # 1. 現在時刻を取得
        now = timezone.now()
        
        # 2. 30秒前の時刻を計算
        time_threshold = now - timedelta(minutes=30)
        
        # 3. 30秒前(time_threshold)以上のcreated_atを持つデータを抽出
        # ※ DBルーターを使用しているようなので .using('team_akb5') を念のため入れています
        return StatusReport.objects.using('team_akb5').filter(
            created_at__gte=time_threshold
        ).order_by('-created_at')

