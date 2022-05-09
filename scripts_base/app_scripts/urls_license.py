from django.urls import path
from app_scripts.views import (
    AddLicenseKeyView, CheckLicenseView, LicenseApproveView, ConfirmLicense, NotConfirmLicense)


urlpatterns = [
    path('checklicense', CheckLicenseView.as_view(), name='checklicense'),
    path('add_license_key', AddLicenseKeyView.as_view(), name='add_license_key'),
    path('confirm_license', ConfirmLicense.as_view(), name='confirm_license'),
    path('not_confirm_license', NotConfirmLicense.as_view(), name='not_confirm_license'),
    path('licenseapprove', LicenseApproveView.as_view(), name='licenseapprove'),
]
