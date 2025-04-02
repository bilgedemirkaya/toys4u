from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import logout_view
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/toys/', permanent=False), name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('toys/', views.toy_list, name='toy_list'),
    path('custom-toy/', views.create_custom_toy, name='create_custom_toy'),
    path('accounts/profile/', RedirectView.as_view(url='/profile/', permanent=False), name='redirect_to_profile'),
    path('cart/add/<int:toy_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/place/<int:order_id>/', views.place_order, name='place_order'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('staff-list/', views.staff_list, name='staff_list'),
    path('grant-admin/<int:user_id>/', views.grant_admin, name='grant_admin'),
    path('staff/revoke-admin/<int:user_id>/', views.revoke_admin, name='revoke_admin'),
]
