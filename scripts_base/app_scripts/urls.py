from django.urls import path, include
from app_scripts.views import BaseView, CheckLicenseView, MyIpView, SecondaryMarketView, LicenseApproveView


urlpatterns = [
    path('', BaseView.as_view(), name='script'),
    path('clients/', include('app_scripts.urls_clients')),
    path('products/', include('app_scripts.urls_product')),
    path('licenses/', include('app_scripts.urls_license')),
    path('my_ip', MyIpView.as_view(), name='my_ip'),
]
