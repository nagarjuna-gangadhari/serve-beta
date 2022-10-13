"""URL Routes for payment
"""
from django.conf.urls import patterns
from django.conf.urls import url
from .views import *


urlpatterns = [ 
    url(r'^login/$', LoginView, name='login'),
    url(r'^logout/$', LogoutView, name='logout'),
    url(r'^signup/$', SignupView, name='signup'),
    url(r'^csrf/?', EnsureCsrf, name='csrf'),
    ]
