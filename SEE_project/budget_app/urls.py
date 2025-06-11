from django.urls import path
from .views import *

urlpatterns = [
    path('calculate/', calculate_view, name='cal'),
    # path('register/', register_view, name='regist'),
]