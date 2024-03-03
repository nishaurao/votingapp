from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from .models import Candidate, Vote


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    ird_number = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=15)
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'first_name', 'last_name', 'ird_number', 'phone', 'dob']
        widgets = {
            'role': forms.HiddenInput(),  # Hide the role field
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['role'] = 'voter'  # Set initial value of role to 'voter'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean_ird_number(self):
        ird_number = self.cleaned_data.get('ird_number')
        if CustomUser.objects.filter(ird_number=ird_number).exists():
            raise forms.ValidationError('This IRD number is already in use.')
        return ird_number



class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name']  

class VotingDatesForm(forms.Form):
    start_date = forms.DateField(label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))

class UpdateVotingDatesForm(forms.Form):
    start_date = forms.DateField(label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['candidate']