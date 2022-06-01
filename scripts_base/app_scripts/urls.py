from django.urls import path, include
from app_scripts.views import (
    BaseView, MyIpView, TestCeleryView)


urlpatterns = [
    path('', BaseView.as_view(), name='script'),
    path('clients/', include('app_scripts.urls_clients')),
    path('products/', include('app_scripts.urls_product')),
    path('licenses/', include('app_scripts.urls_license')),
    path('my_ip', MyIpView.as_view(), name='my_ip'),
    path('test', TestCeleryView.as_view(), name='test'),
]
