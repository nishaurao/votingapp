from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CandidateForm
from .forms import UserRegisterForm
from .models import Candidate,Vote




# Create your views here.

def register_view(request):
    User = get_user_model()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create user object without saving to DB
            user.set_password(form.cleaned_data['password1'])  # Set password
            user.save()  # Save user to DB
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    user = request.user
    return render(request, 'accounts/profile.html')


@login_required
def user_details(request):
    return render(request, 'accounts/user_details.html')


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('profile')  
    else:
        candidates = Candidate.objects.all()
        candidate_votes = {candidate.name: Vote.objects.filter(candidate=candidate).count() for candidate in candidates}
        return render(request, 'accounts/admin_dashboard.html', {'candidates': candidates, 'candidate_votes': candidate_votes})
    return render(request, 'accounts/admin_dashboard.html')


@login_required
def add_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate_name = form.cleaned_data['name']
            if Candidate.objects.filter(name=candidate_name).exists():
                # Candidate with the same name already exists
                error_message = "Candidate with this name already exists."
                return render(request, 'accounts/add_candidate.html', {'form': form, 'error_message': error_message})
            else:
                # No duplicate candidate found, save the candidate
                form.save()
                return redirect('admin_dashboard')  # Adjust the redirect URL as needed
    else:
        form = CandidateForm()
    return render(request, 'accounts/add_candidate.html', {'form': form})


@login_required
def reset_candidates(request):
    Candidate.objects.all().delete()
    return redirect('admin_dashboard')  # Adjust the redirect URL as needed


@login_required
def add_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate_name = form.cleaned_data['name']
            if Candidate.objects.filter(name=candidate_name).exists():
                # Candidate with the same name already exists
                error_message = "Candidate with this name already exists."
                return render(request, 'accounts/add_candidate.html', {'form': form, 'error_message': error_message})
            else:
                # No duplicate candidate found, save the candidate
                form.save()
                return redirect('admin_dashboard')  # Adjust the redirect URL as needed
    else:
        form = CandidateForm()
    return render(request, 'accounts/add_candidate.html', {'form': form})

