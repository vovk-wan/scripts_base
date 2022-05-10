from django.urls import path
from app_scripts.views import SecondaryMarketView, AddProductView, GetAllProductsView


urlpatterns = [
    path('add_product', AddProductView.as_view(), name='add_product'),
    path('get_all_products', GetAllProductsView.as_view(), name='get_all_products'),
    path('secondary', SecondaryMarketView.as_view(), name='secondary_market'),
]

