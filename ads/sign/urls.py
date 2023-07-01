from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import login_view, LogoutViewCustom, register_user, code, InvalidCode

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', LogoutViewCustom, name='logout'),
    path('signup/', register_user, name='signup'),
    path('code/', code, name='code'),
    path('code/invalid/', InvalidCode.as_view(), name='invalid_code'),
]