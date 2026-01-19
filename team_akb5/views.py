from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Member, StatusReport
from .forms import StatusReportForm
from django.views.generic import CreateView, ListView
from django.utils import timezone
from datetime import timedelta
import json


def index(request):
    return render(request, "teams/team_akb5/index.html")


def members(request):
    qs = Member.objects.using("team_akb5").all()  # ← team_terrace DBを明示
    return render(request, "teams/team_akb5/members.html", {"members": qs})


def reports(request):
    qs = StatusReport.objects.using("team_akb5").all()
    return render(request, "teams/team_akb5/status_report_form.html")


class AdminView(ListView):
    model = StatusReport
    template_name = "teams/team_akb5/admin.html"
    context_object_name = "reports"
    ordering = ["-created_at"]

    def post(self, request, *args, **kwargs):
        report_id = request.POST.get("report_id")
        if report_id:
            report = StatusReport.objects.using("team_akb5").get(id=report_id)
            report.delete()
        return redirect("team_akb5:admin")


class StatusReportCreateView(CreateView):
    model = StatusReport
    form_class = StatusReportForm
    template_name = "teams/team_akb5/status_report_form.html"
    success_url = reverse_lazy("team_akb5:admin")


class UserView(ListView):
    model = StatusReport
    template_name = "teams/team_akb5/user.html"
    context_object_name = "reports"

    def get_queryset(self):
        """
        直近30秒以内に作成されたレポートのみを返す
        """
        now = timezone.now()
        time_threshold = now - timedelta(minutes=30)
        return (
            StatusReport.objects.using("team_akb5")
            .filter(created_at__gte=time_threshold)
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get reports with location data from the initial queryset
        reports_with_location = (
            self.get_queryset()
            .exclude(latitude__isnull=True)
            .exclude(longitude__isnull=True)
        )

        features = []
        for report in reports_with_location:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [report.longitude, report.latitude],
                    },
                    "properties": {
                        "symptom": report.get_symptom_display(),
                        "floor": report.floor,
                        "description": report.description,
                        "timestamp": report.timestamp.isoformat(),
                    },
                }
            )

        context["reports_geojson"] = json.dumps(
            {"type": "FeatureCollection", "features": features}
        )
        return context
