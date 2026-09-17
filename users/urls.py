from django.urls import path
from .views import UserRegisterView, UserLoginView, UserLogoutView, PublicProfileView, profile_view

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('<slug:username>/', PublicProfileView.as_view(), name='public_profile'),
]
