from django.urls import path
from . import views
from .views import CustomerLoginView, CustomerRegistration


app_name = 'store'


urlpatterns = [

        path('', views.store, name="home"),
        path('cart/', views.cart, name="cart"),
        path('checkout/', views.checkout, name="checkout"),
        path('update_item/', views.updateItem, name="update_item"),
        path('process_order/', views.processOrder, name="process_order"),

        path('login/', CustomerLoginView.as_view(), name="customerlogin"),
        path('register/', CustomerRegistration.as_view(), name="customerregistration"),

]