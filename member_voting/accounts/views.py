from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CandidateForm
from .forms import UserRegisterForm
from .models import Candidate,Vote,VotingSettings,CustomUser
from .forms import VotingDatesForm
from .forms import UpdateVotingDatesForm
from .forms import VoteForm
from datetime import datetime,date
from django.utils import timezone
import datetime

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
    has_voted = Vote.objects.filter(user=user).exists()
    voting_settings = VotingSettings.objects.first()
    context = {'has_voted': has_voted, 'vote_set':voting_settings}
    return render(request, 'accounts/profile.html', context)



@login_required
def user_details(request):
    user = request.user
    return render(request, 'accounts/user_details.html')



@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('profile')  
    else:
        candidates = Candidate.objects.all()
        candidate_votes = {candidate.name: Vote.objects.filter(candidate=candidate).count() for candidate in candidates}
        return render(request, 'accounts/admin_dashboard.html', {'candidates': candidates, 'candidate_votes': candidate_votes})
    return render(request, 'accounts/admin_dashboard.html',{'candidates': candidates})


@login_required
def add_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate_name = form.cleaned_data['name']
            if Candidate.objects.filter(name=candidate_name).exists():
                # Candidate with the same name already exists
                error_message = "Candidate with this name already exists."
                return render(request, 'accounts/add_candidate.html', {'form': form, 'error_message': error_message}, status=200)
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


# @login_required
# def add_candidate(request):
#     if request.method == 'POST':
#         form = CandidateForm(request.POST)
#         if form.is_valid():
#             candidate_name = form.cleaned_data['name']
#             if Candidate.objects.filter(name=candidate_name).exists():
#                 # Candidate with the same name already exists
#                 error_message = "Candidate with this name already exists."
#                 return render(request, 'accounts/add_candidate.html', {'form': form, 'error_message': error_message})
#             else:
#                 # No duplicate candidate found, save the candidate
#                 form.save()
#                 return redirect('admin_dashboard')  # Adjust the redirect URL as needed
#     else:
#         form = CandidateForm()
#     return render(request, 'accounts/add_candidate.html', {'form': form})


@login_required
def set_voting_dates(request):  
    if VotingSettings.objects.exists():
        # Voting dates are already set, redirect to the update voting page
        return redirect('update_voting_dates')
    
    if request.method == 'POST':
        form = VotingDatesForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            if start_date < end_date:
                # Save the voting dates to the database
                VotingSettings.objects.create(start_date=start_date, end_date=end_date)
                # Add a success message
                messages.success(request, "Voting dates successfully set.")
                # Redirect to success page
                return redirect('setdate_success')  
            else:
                messages.error(request, "End date must be greater than start date.")
        else:
            messages.error(request, "Invalid form submission. Please correct the errors.")
    else:
        form = VotingDatesForm()
    
    return render(request, 'accounts/set_voting_dates.html', {'form': form})



@login_required
def update_voting_dates(request):
    try:
        current_settings = VotingSettings.objects.get(pk=1) # this will handle only single poll event. we can enhance the functionlity to make it multiple events
    except VotingSettings.DoesNotExist:
        current_settings = None

    if request.method == 'POST':
        form = UpdateVotingDatesForm(request.POST)
        if form.is_valid():
            new_start_date = form.cleaned_data['start_date']
            new_end_date = form.cleaned_data['end_date']
            
            if new_start_date < new_end_date:
                try:
                    if current_settings:
                        current_settings.start_date = new_start_date
                        current_settings.end_date = new_end_date
                        current_settings.save()
                    else:
                        VotingSettings.objects.create(start_date=new_start_date, end_date=new_end_date)
                    return redirect('setdate_success')
                except Exception as e:
                    print("Error updating voting dates:", e)
            else:
                messages.error(request, "End date must be greater than start date.")
        else:
            print("Form errors:", form.errors)
    else:
        initial_data = {'start_date': current_settings.start_date, 'end_date': current_settings.end_date} if current_settings else None
        form = UpdateVotingDatesForm(initial=initial_data)

    return render(request, 'accounts/update_voting_dates.html', {'form': form})


def setdate_success(request):
    return render(request, 'accounts/setdate_success.html')





@login_required
def vote(request):
    try:
        current_settings = VotingSettings.objects.get(pk=1)
    except VotingSettings.DoesNotExist:
        return render(request, 'accounts/voting_not_allowed.html')  # Handle the case where voting settings are not available

    start_date = current_settings.start_date
    end_date = current_settings.end_date
    current_datetime = datetime.datetime.now()

    if not (start_date <= current_datetime.date() <= end_date):
        return render(request, 'accounts/voting_not_allowed.html')  # Render a template indicating that voting is not allowed


    if request.method == 'POST':
        form = VoteForm(request.POST)

        if form.is_valid():
            # Validate user age
            date_of_birth = request.user.dob  # Assuming user profile has date_of_birth field
            today = date.today()

            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            if age < 18:
                messages.error(request, "Voting is allowed only for users 18 years or older.")
                return redirect('vote')  # Redirect back to vote page with error message

            # Check if a candidate is selected
            if not form.cleaned_data['candidate']:
                messages.error(request, "Please select a candidate to vote.")
                return redirect('vote')  # Redirect back to vote page with error message
            
            form.instance.user = request.user
            form.save()
            return redirect('thank_you')  # Redirect to thank you page
        else:
            messages.error(request, "Please select a candidate to vote.")
            return redirect('vote')  

    else:
        form = VoteForm()
    
    candidates = Candidate.objects.all()
    return render(request, 'accounts/vote.html', {'form': form, 'candidates': candidates})

@login_required
def thank_you(request):
    return render(request, 'accounts/thank_you.html')

@login_required
def voting_not_allowed(request):
    return render(request, 'accounts/voting_not_allowed.html')

@login_required
def customuser_list(request):
    users = CustomUser.objects.all()
    return render(request, 'accounts/customuser_list.html', {'users': users})
