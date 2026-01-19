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

class RoadmapListView(LoginRequiredMixin, ListView):
    model = Roadmap
    login_url = 'login/'
    template_name = 'teams/team_TMR/career/roadmap_list.html'
    context_object_name = 'roadmaps'

    def get_queryset(self):
        return Roadmap.objects.filter(user_id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        raw_roadmaps = context['roadmaps']
        gantt_data = []
        for r in raw_roadmaps:
            months_active = []
            for m in range(1, 13):
                is_active = False
                if r.start_date and r.end_date:
                    s_m = r.start_date.month
                    e_m = r.end_date.month
                    if s_m <= e_m:
                        if s_m <= m <= e_m: is_active = True
                    else:
                        if m >= s_m or m <= e_m: is_active = True
                months_active.append(is_active)
            gantt_data.append({'obj': r, 'months': months_active})
        context['gantt_data'] = gantt_data
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