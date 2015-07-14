from django.contrib import admin
from django import forms
from django.forms.widgets import *
from django.db import models
from django.forms.formsets import formset_factory, BaseFormSet
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm

# Snippet import to use the admin FilterSelectMultiple widget in normal forms
from django.contrib.admin.widgets import FilteredSelectMultiple

# Import from general utilities
from util import *

from mhcdashboardapp.models import *

# User Forms
class UserProfileForm(UserChangeForm):
    class Meta:
        model = User
        exclude = ('groups','is_staff','is_active','is_superuser','user_permissions','last_login','date_joined',) 
