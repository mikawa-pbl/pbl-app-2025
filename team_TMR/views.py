from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from datetime import date

from .models import Profile, Roadmap, ES, InvitationCode
from .forms import ProfileForm, RoadmapForm, ESForm, InvitationCodeForm, DEFAULT_CODES

class SignUpView(View):
    def get(self, request):
        invitation_form = InvitationCodeForm()
        user_form = UserCreationForm()
        return render(request, 'teams/team_TMR/registration/signup.html', {
            'invitation_form': invitation_form,
            'user_form': user_form
        })

    def post(self, request):
        invitation_form = InvitationCodeForm(request.POST)
        user_form = UserCreationForm(request.POST)

        if invitation_form.is_valid() and user_form.is_valid():
            code_str = invitation_form.cleaned_data.get('invitation_code')
            if code_str not in DEFAULT_CODES:
                try:
                    invitation_code = InvitationCode.objects.get(code=code_str, used=False)
                    invitation_code.used = True
                    invitation_code.save()
                except InvitationCode.DoesNotExist:
                    pass 
            user = user_form.save()
            return redirect(reverse_lazy('login'))
        return render(request, 'teams/team_TMR/registration/signup.html', {
            'invitation_form': invitation_form,
            'user_form': user_form
        })

class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'teams/team_TMR/career/profile.html'
    success_url = reverse_lazy('profile')
    def get_object(self):
        return Profile.objects.filter(user_id=self.request.user.id).first()

from django.core.serializers.json import DjangoJSONEncoder
import json

class RoadmapListView(LoginRequiredMixin, ListView):
    model = Roadmap
    login_url = '/team_TMR/login/'
    template_name = 'teams/team_TMR/career/roadmap_list.html'
    context_object_name = 'roadmaps'

    def get_queryset(self):
        return Roadmap.objects.filter(user_id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['target_user'] = self.request.user
        context['is_owner'] = True
        raw_roadmaps = context['roadmaps']
        
        # Frappe Gantt用のデータ作成
        tasks = []
        for r in raw_roadmaps:
             if r.start_date and r.end_date:
                # 日付の順序が逆の場合は入れ替える
                start = r.start_date
                end = r.end_date
                if start > end:
                    start, end = end, start

                tasks.append({
                    'id': str(r.id),
                    'name': r.title,
                    'start': start.isoformat(),
                    'end': end.isoformat(),
                    'progress': 0,
                    'custom_class': 'bar-blue',
                    'description': r.content,
                })
        context['tasks_json'] = json.dumps(tasks, cls=DjangoJSONEncoder)
        return context

class RoadmapCreateView(LoginRequiredMixin, CreateView):
    model = Roadmap
    form_class = RoadmapForm
    template_name = 'teams/team_TMR/career/roadmap_form.html'
    success_url = reverse_lazy('roadmap_list')
    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        return super().form_valid(form)

class RoadmapUpdateView(LoginRequiredMixin, UpdateView):
    model = Roadmap
    form_class = RoadmapForm
    template_name = 'teams/team_TMR/career/roadmap_form.html'
    success_url = reverse_lazy('roadmap_list')
    def get_queryset(self):
        return Roadmap.objects.filter(user_id=self.request.user.id)

class RoadmapDeleteView(LoginRequiredMixin, DeleteView):
    model = Roadmap
    template_name = 'teams/team_TMR/career/roadmap_confirm_delete.html'
    success_url = reverse_lazy('roadmap_list')
    def get_queryset(self):
        return Roadmap.objects.filter(user_id=self.request.user.id)

# ES関連ビュー (ESListView, ESCreateView, ESUpdateView, ESDeleteView) は
# 基本的にRoadmapと同様に user_id=self.request.user.id を使用して実装されています。
class ESListView(LoginRequiredMixin, ListView):
    model = ES
    template_name = 'teams/team_TMR/career/es_list.html'
    context_object_name = 'es_entries'
    def get_queryset(self): return ES.objects.filter(user_id=self.request.user.id)

class ESCreateView(LoginRequiredMixin, CreateView):
    model = ES
    form_class = ESForm
    template_name = 'teams/team_TMR/career/es_form.html'
    success_url = reverse_lazy('es_list')
    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        return super().form_valid(form)

class ESUpdateView(LoginRequiredMixin, UpdateView):
    model = ES
    form_class = ESForm
    template_name = 'teams/team_TMR/career/es_form.html'
    success_url = reverse_lazy('es_list')
    def get_queryset(self): return ES.objects.filter(user_id=self.request.user.id)

class ESDeleteView(LoginRequiredMixin, DeleteView):
    model = ES
    template_name = 'teams/team_TMR/career/es_confirm_delete.html'
    success_url = reverse_lazy('es_list')
    def get_queryset(self): return ES.objects.filter(user_id=self.request.user.id)

class MemberListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'teams/team_TMR/members.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        # 自分以外のユーザーも含めてリスト表示
        queryset = Profile.objects.all().order_by('graduation_year')

        # 検索パラメータの取得
        q_nickname = self.request.GET.get('query_nickname')
        q_lab = self.request.GET.get('query_lab')
        q_field = self.request.GET.get('query_field')
        q_decision = self.request.GET.get('query_decision')

        # フィルタリング (AND条件)
        if q_nickname:
            queryset = queryset.filter(nickname__icontains=q_nickname)
        if q_lab:
            queryset = queryset.filter(lab__icontains=q_lab)
        if q_field:
            queryset = queryset.filter(research_field__icontains=q_field)
        if q_decision:
            queryset = queryset.filter(decision__icontains=q_decision)

        return queryset

class MemberRoadmapView(LoginRequiredMixin, ListView):
    model = Roadmap
    template_name = 'teams/team_TMR/career/roadmap_list.html'
    context_object_name = 'roadmaps'

    def get_queryset(self):
        # URLのpkで指定されたユーザーのロードマップを取得
        user_id = self.kwargs.get('pk')
        return Roadmap.objects.filter(user_id=user_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get('pk')
        target_user = get_object_or_404(User, pk=user_id)
        
        # 閲覧対象のユーザー情報を渡す
        context['target_user'] = target_user
        context['is_owner'] = (self.request.user.id == target_user.id)

        # Frappe Gantt用のデータ作成
        raw_roadmaps = context['roadmaps']
        tasks = []
        for r in raw_roadmaps:
             if r.start_date and r.end_date:
                # 日付の順序が逆の場合は入れ替える
                start = r.start_date
                end = r.end_date
                if start > end:
                    start, end = end, start

                tasks.append({
                    'id': str(r.id),
                    'name': r.title,
                    'start': start.isoformat(),
                    'end': end.isoformat(),
                    'progress': 0,
                    'custom_class': 'bar-blue',
                    'description': r.content,
                })
        context['tasks_json'] = json.dumps(tasks, cls=DjangoJSONEncoder)
        return context