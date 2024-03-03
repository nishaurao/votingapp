from django.contrib.sessions.middleware import SessionMiddleware

from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.urls import reverse
from accounts.models import CustomUser 
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib import messages
from accounts.forms import UserRegisterForm
from accounts.views import register_view
from django.shortcuts import render, redirect
from accounts.models import Candidate,Vote
from accounts.forms import CandidateForm
from accounts.views import add_candidate,set_voting_dates,thank_you
from accounts.views import reset_candidates,setdate_success, voting_not_allowed,user_details, profile_view
from django.contrib.auth.models import AnonymousUser
from datetime import date
from unittest.mock import patch
from accounts.models import VotingSettings
from django.http import HttpResponseRedirect
from django.contrib.messages import get_messages
from django.utils import timezone
from .views import update_voting_dates
from .forms import UpdateVotingDatesForm
from .forms import VoteForm
from .views import vote
from django.contrib.auth.models import Group




# Create your tests here.

class RegisterViewTestCase(TestCase):
    def setUp(self):
        self.register_url = reverse('register')

    def test_register_view_post(self):
        # Define POST data for registration form
        data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'testuser@example.com',  
            'first_name': 'John',              
            'last_name': 'Doe', 
            'dob': '1999-09-09' ,
            'irb_number': '1123',
            'phone': '1111111',
        }

        # Make POST request to register URL with form data
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200) #check if response is success



    def test_register_view_get(self):
        # Make GET request to register URL
        response = self.client.get(self.register_url)

        # Check if registration form is rendered
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')


    def test_register_view_post_with_invalid_data(self):
        # Define invalid POST data with an empty username
        invalid_data = {
            'username': '',  # Invalid: empty username
            'email': 'test@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

        # Make a POST request to the register URL with invalid form data
        response = self.client.post(self.register_url, invalid_data)

        # Check if the response status code is 200 (form rendering)
        self.assertEqual(response.status_code, 200)

        # Check if the form is rendered with errors
        form = response.context['form']
        self.assertTrue(form.errors)  # Check if form has errors
        self.assertIn('username', form.errors)  # Check if 'username' field has errors
        self.assertEqual(form.errors['username'], ['This field is required.'])  # Check specific error message



class LoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password123'}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('profile'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertContains(response, 'Invalid username or password.')


class UserDetailsViewTestCase(TestCase):
    
    def setUp(self):
        # Create a user for testing
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

    def test_user_details_view_authenticated(self):
        # Make a GET request to the profile_view view as an authenticated user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_details'))

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'accounts/user_details.html')

    def test_user_details_not_authenticated(self):
        # Make a GET request to the profile_view view as an anonymous user
        request = RequestFactory().get(reverse('user_details'))
        request.user = AnonymousUser()
        response = profile_view(request)

        # Check if the response status code is 302 (redirects to login page)
        self.assertEqual(response.status_code, 302)

        # Check if the user is redirected to the login page
        self.assertIn('/accounts/login/', response.url)




class ProfileViewTestCase(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

    def test_profile_view_authenticated(self):
        # Make a GET request to the profile_view view as an authenticated user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('profile'))

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_view_not_authenticated(self):
        # Make a GET request to the profile_view view as an anonymous user
        request = RequestFactory().get(reverse('profile'))
        request.user = AnonymousUser()
        response = profile_view(request)

        # Check if the response status code is 302 (redirects to login page)
        self.assertEqual(response.status_code, 302)

        # Check if the user is redirected to the login page
        self.assertIn('/accounts/login/', response.url)


class ThankYouViewTestCase(TestCase):
       
    def setUp(self):
        # Create a user for testing
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

    def test_thank_you_view(self):
        # Make a GET request to the profile_view view as an authenticated user
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('thank_you'))

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'accounts/thank_you.html')

    def test_thank_you_view_not_authenticated(self):
        # Make a GET request to the thank_you view as an anonymous user
        request = RequestFactory().get(reverse('thank_you'))
        request.user = AnonymousUser()
        response = thank_you(request)

        # Check if the response status code is 302 (redirects to login page)
        self.assertEqual(response.status_code, 302)

        # Check if the user is redirected to the login page
        self.assertIn('/accounts/login/', response.url)


class LogoutViewTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        # Login the user
        self.client.login(username='testuser', password='testpassword')

    def test_logout_view(self):
        # Make a GET request to the logout view
        response = self.client.get(reverse('logout'))
        # Check that the response is a redirect
        self.assertEqual(response.status_code, 302)
        # Check that the user is redirected to the login page
        self.assertEqual(response.url, reverse('login'))
        # Check that the user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def tearDown(self):
        # Delete the user
        self.user.delete()
    
    def test_logout_view_when_not_logged_in(self):
        # Make a GET request to the logout view when not logged in
        response = self.client.get(reverse('logout'))
        # Check that the response is a redirect
        self.assertEqual(response.status_code, 302)
        # Check that the user is redirected to the login page
        self.assertEqual(response.url, reverse('login'))
        # Check that the user remains logged out (i.e., no error occurs)
        self.assertFalse(response.wsgi_request.user.is_authenticated)




class AddCandidateViewTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser', password='password'
        )


    def test_add_candidate_duplicate(self):
        # Login the user
        self.client.login(username='testuser', password='password')

        # Create an existing candidate
        existing_candidate = Candidate.objects.create(name='James avery')

        # Get the URL for the add candidate view
        url = reverse('add_candidate')

        # Create a POST request with form data for an existing candidate
        data = {
            'name': existing_candidate.name,
        }
        response = self.client.post(url, data)

        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check that the error message is displayed in the response content
        self.assertContains(response, "Candidate with this name already exists.")

    def test_add_candidate_new(self):
        # Login the user
        self.client.login(username='testuser', password='password')

        # Get the URL for the add candidate view
        url = reverse('add_candidate')

        # Create a POST request with form data for a new candidate
        data = {
            'name': 'New Candidate',
        }
        response = self.client.post(url, data)

        # Check that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Check that the candidate is saved to the database
        new_candidate = Candidate.objects.filter(name='New Candidate').first()
        self.assertIsNotNone(new_candidate)




class AdminDashboardViewTestCase(TestCase):
    def setUp(self):
        # Create a test user (non-admin)
        self.user_non_admin = CustomUser.objects.create_user(
            username='nonadmin', password='password'
        )

        # Create a test user with admin role
        self.user_admin = CustomUser.objects.create_user(
            username='admin', password='password'
        )
        

    def test_admin_dashboard_logged_in_admin(self):
        # Login the admin user
        self.client.login(username='admin', password='password')

        # Get the URL for the admin dashboard view
        url = reverse('admin_dashboard')

        # Send a GET request to the admin dashboard view
        response = self.client.get(url)

        # Check that the response status code is 200
        self.assertEqual(response.status_code, 302)

      

    def test_admin_dashboard_logged_in_non_admin(self):
        # Login the non-admin user
        self.client.login(username='nonadmin', password='password')

        # Get the URL for the admin dashboard view
        url = reverse('admin_dashboard')

        # Send a GET request to the admin dashboard view
        response = self.client.get(url)

        # Check that the response redirects to the profile page
        self.assertRedirects(response, reverse('profile'))



class SetVotingDatesViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

    def test_set_voting_dates_logged_in(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')
        
        # Make a GET request to the set_voting_dates view
        response = self.client.get(reverse('set_voting_dates'))
        
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check if the 'form' variable is present in the context
        self.assertIn('form', response.context)
        
        # Check if the user is redirected if voting settings already exist
        VotingSettings.objects.create(start_date='2024-01-01', end_date='2024-01-05')
        response = self.client.get(reverse('set_voting_dates'))
        self.assertRedirects(response, reverse('update_voting_dates'))


    def test_set_voting_dates_not_authenticated(self):
        # Make a GET request to the profile_view view as an anonymous user
        request = RequestFactory().get(reverse('set_voting_dates'))
        request.user = AnonymousUser()
        response = set_voting_dates(request)

        # Check if the response status code is 302 (redirects to login page)
        self.assertEqual(response.status_code, 302)

        # Check if the user is redirected to the login page
        self.assertIn('/accounts/login/', response.url)



class VoteViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword', dob='2000-01-01')

    def test_vote_logged_in(self):
        # Log in the user
        self.client.login(username='testuser', password='testpassword')
        
        # Set up VotingSettings
        VotingSettings.objects.create(start_date='2024-01-01', end_date='2024-01-05')
        
        # Make a GET request to the vote view
        response = self.client.get(reverse('vote'))
        
        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Make a POST request to the vote view with valid form data
        candidate = Candidate.objects.create(name='Test Candidate')
        data = {'candidate': candidate.id}
        response = self.client.post(reverse('vote'), data)
        
        self.assertEqual(response.status_code, 200)

    def test_vote_view_not_authenticated(self):
        # Make a GET request to the thank_you view as an anonymous user
        request = RequestFactory().get(reverse('vote'))
        request.user = AnonymousUser()
        response = vote(request)

        # Check if the response status code is 302 (redirects to login page)
        self.assertEqual(response.status_code, 302)

        # Check if the user is redirected to the login page
        self.assertIn('/accounts/login/', response.url)
