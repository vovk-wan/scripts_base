from django.urls import path
from app_scripts.views import BaseView, CheckLicenseView, MyIpView, SecondaryMarketView, LicenseApproveView


urlpatterns = [
    path('', BaseView.as_view(), name='script'),
    path('secondary', SecondaryMarketView.as_view(), name='secondary_market'),
    path('checklicense', CheckLicenseView.as_view(), name='checklicense'),
    path('licenseapprove', LicenseApproveView.as_view(), name='licenseapprove'),
    path('myip', MyIpView.as_view(), name='myip'),
]
