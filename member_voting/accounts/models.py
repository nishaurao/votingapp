from django.db import models

# Create your models here.
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.conf import settings
from django.db import models

#This create a table for candidate in the database
class Candidate(models.Model):
    name = models.CharField(max_length=100)# this is the field to store candidate name

    # this method is to  return the value of the name field for candidate table
    def __str__(self):
        return self.name


#This create a table for vote in the database
class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)


#This create a table for user details in the database
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('voter', 'Voter'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='voter') #here role is defaulted to 'voter' during registration
    ird_number = models.CharField(max_length=30, default='')  
    first_name = models.CharField(max_length=30, default='' )
    last_name = models.CharField(max_length=30, default='')
    phone = models.CharField(max_length=15, default='')
    dob = models.DateField(null=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')

#This create a table for votingdates in the database
class VotingSettings(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
