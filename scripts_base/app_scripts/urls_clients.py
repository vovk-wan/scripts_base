from django.urls import path, include
from app_scripts.views import CheckLicenseView


urlpatterns = [

    path('checklicense', CheckLicenseView.as_view(), name='checklicense'),

]
