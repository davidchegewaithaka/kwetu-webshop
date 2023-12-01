from django.urls import path
from .views import index, add_to_cart, view_cart,remove_from_cart, checkout, register, user_login, user_logout
from django.contrib.auth.views import LogoutView  # Import the LogoutView


urlpatterns = [
    path('', index, name='index'),
    path('remove_from_cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('view_cart/', view_cart, name='view_cart'),
    path('checkout/', checkout, name='checkout'),
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),  # Update this line
]