from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from home import views
from . import views
from .views import CustomLoginView
from .views import CustomLogoutView 



urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about, name="about"),
    path("blog_single", views.blog_single, name="blog_single"),
    path("blog", views.blog_list, name="blog"),
    path("contact", views.contact, name="contact"),
    path("destination", views.destination, name="destination"),
    path("hotel", views.hotel, name="hotel"),
    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('profile/', views.profile_view, name='profile'),
    path('search/', views.search_packages, name='search_packages'),
    path('add-to-cart/<int:package_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:package_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
    


