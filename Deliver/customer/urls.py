from django.urls import path
from .views import register_re, re_login,home,logout,delete

urlpatterns = [
    path('register_re/',register_re,name='register_re'),
    path('re_login/',re_login,name='re_login'),
    path('logout',logout,name='logout'),
    path('home/',home,name='home'),
    path('delete/<int:id>/',delete,name='delete')
]
