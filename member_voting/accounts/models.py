from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.conf import settings

from django.db import models

# class UserProfile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     # Add any additional fields you want for your user profile


class Candidate(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

 
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('voter', 'Voter'),
        ('admin', 'Admin'),
        # Add more roles as needed
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='voter')
    ird_number = models.CharField(max_length=30, default='')  # Add the IRD number field

    # Add first_name and last_name fields
    first_name = models.CharField(max_length=30, default='' )
    last_name = models.CharField(max_length=30, default='')
    phone = models.CharField(max_length=15, default='')
    dob = models.DateField(null=True)
    
    # Specify unique related_name for groups and user_permissions
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')

class VotingSettings(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()