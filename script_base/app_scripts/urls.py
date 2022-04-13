from django.urls import path, include
from app_scripts.views import BaseView


urlpatterns = [
    path('', BaseView.as_view(), name='script'),
]
