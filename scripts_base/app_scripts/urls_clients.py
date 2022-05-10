from django.urls import path, include
from app_scripts.views import BaseView, CheckLicenseView, MyIpView, SecondaryMarketView, LicenseApproveView


urlpatterns = [

    path('checklicense', CheckLicenseView.as_view(), name='checklicense'),

]
