from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User
from apps.generator.models import GenerationRequest


class RegisterView(CreateView):
    """Регистрация пользователя"""
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        login(self.request, user)
        messages.success(self.request, 'Регистрация прошла успешно!')
        return response


@login_required
def dashboard(request):
    """Личный кабинет пользователя"""
    generations = GenerationRequest.objects.filter(user=request.user).order_by('-created_at')[:10]

    context = {
        'user': request.user,
        'generations': generations,
        'can_generate': request.user.can_generate(),
    }
    return render(request, 'users/dashboard.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('users:dashboard')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})