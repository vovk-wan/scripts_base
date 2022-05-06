from django.urls import path
from app_scripts.views import BaseView, CheckLicenseView, MyIpView, SecondaryMarketView


urlpatterns = [
    path('', BaseView.as_view(), name='script'),
    path('secondary_market', SecondaryMarketView.as_view(), name='/secondary_market'),
    path('chek', CheckLicenseView.as_view(), name='check'),
    path('myip', MyIpView.as_view(), name='myip'),
]
