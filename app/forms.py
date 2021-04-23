from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Customer


class CustomerRegistrationForm(UserCreationForm):
	email=forms.EmailField()
	class Meta:
		model = User
		fields = ['username','email','password1','password2']
		help_texts={
		'username':None,
		}	

class CustomerProfileForm(forms.ModelForm):
	class Meta:
		model = Customer
		fields = ['name','locality','city','zipcode','state']