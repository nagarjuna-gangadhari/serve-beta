from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^wall/', views.feed_posting, name='feed_posting'),
    url(r'^create_user/', views.create_user, name='create_user'),
]
