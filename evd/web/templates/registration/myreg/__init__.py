from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User
from django import forms

from registration import signals
from registration.forms import RegistrationForm

class MyRegBackend(object):
    def register(self, request, **kwargs):
        print **kwargs
