from django.urls import path
from app_scripts.views import BaseView, Check


urlpatterns = [
    path('', BaseView.as_view(), name='script'),
    path('chek/', Check.as_view(), neme='check'),
]
