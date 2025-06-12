from django.urls import path
from .views import *

urlpatterns = [
    path('pic/', pic_view, name='pic'),
]

