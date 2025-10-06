from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from .models import Todo
from .forms import TodoForm, CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordChangeForm, CustomPasswordResetForm, UserProfileForm

# Create your views here.
@login_required
def home(request):
    form = TodoForm()
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    view = request.GET.get('view', '')
    
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            messages.success(request, f'Task "{todo.text}" created successfully!')
            return redirect('home')
    
    # Get user's todos
    user_todos = Todo.objects.filter(user=request.user)
    
    # Apply search filter if search query exists
    if search_query:
        user_todos = user_todos.filter(text__icontains=search_query)
    
    # Organize todos by date
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    today_todos = user_todos.filter(due_date=today) | user_todos.filter(due_date__isnull=True, created_at__date=today)
    tomorrow_todos = user_todos.filter(due_date=tomorrow)
    upcoming_todos = user_todos.filter(due_date__gt=tomorrow)
    overdue_todos = user_todos.filter(due_date__lt=today, completed=False)
    completed_todos = user_todos.filter(completed=True)
    
    # Category filtering
    if category:
        current_todos = user_todos.filter(category=category)
    elif view == 'upcoming':
        current_todos = upcoming_todos
    elif view == 'today':
        current_todos = today_todos
    elif view == 'completed':
        current_todos = completed_todos
    elif view == 'missed':
        current_todos = overdue_todos  # Missed tasks are overdue incomplete tasks
    else:
        current_todos = today_todos
    
    # Get counts for sidebar
    personal_count = user_todos.filter(category='personal').count()
    work_count = user_todos.filter(category='work').count()
    home_count = user_todos.filter(category='home').count()
    completed_count = user_todos.filter(completed=True).count()
    missed_count = user_todos.filter(due_date__lt=today, completed=False).count()
    
    context = {
        'form': form,
        'today_todos': today_todos,
        'tomorrow_todos': tomorrow_todos,
        'upcoming_todos': upcoming_todos,
        'overdue_todos': overdue_todos,
        'completed_todos': completed_todos,
        'current_todos': current_todos,
        'search_query': search_query,
        'category': category,
        'view': view,
        'today_date': today,
        'personal_count': personal_count,
        'work_count': work_count,
        'home_count': home_count,
        'completed_count': completed_count,
        'missed_count': missed_count,
    }
    return render(request, 'myapp/index_new.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('email')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'myapp/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})

@login_required
def logout_view(request):
    user_name = request.user.first_name or request.user.username
    logout(request)
    messages.info(request, f'Goodbye, {user_name}! You have been logged out.')
    return redirect('login')

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'myapp/edit_profile.html', {'form': form})

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'myapp/change_password.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password was successfully updated!')
        return super().form_valid(form)

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'myapp/forgot_password.html'
    success_url = reverse_lazy('password_reset_done')
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'myapp/reset_password_confirm.html'
    success_url = reverse_lazy('login')

@login_required
def add_todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            if hasattr(todo, 'user'):
                todo.user = request.user
            todo.save()
    return redirect('home')

@login_required
def toggle_todo(request, todo_id):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, id=todo_id, user=request.user) if hasattr(Todo, 'user') else get_object_or_404(Todo, id=todo_id)
        todo.completed = not todo.completed
        todo.save()
        status = "completed" if todo.completed else "marked as pending"
        messages.success(request, f'Task "{todo.text}" {status}!')
    return redirect('home')

@login_required
def edit_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task updated successfully!')
            return redirect('home')
    else:
        form = TodoForm(instance=todo)
    
    context = {
        'form': form,
        'todo': todo,
        'is_edit': True
    }
    return render(request, 'myapp/edit_todo.html', context)

@login_required
def delete_todo(request, todo_id):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, id=todo_id, user=request.user)
        todo.delete()
        messages.success(request, f'Task "{todo.text}" deleted successfully!')
    return redirect('home')