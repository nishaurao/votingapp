from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser 




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
    def test_user_details_view(self):
        # Make a GET request to the user_details view
        response = self.client.get(reverse('user_details'))

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'accounts/user_details.html')