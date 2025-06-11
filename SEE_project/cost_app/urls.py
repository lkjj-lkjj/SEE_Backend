from django.urls import path
from .views import *

urlpatterns = [
    path('Delphi/', Delphi_view, name='Delphi'),
    path('Expert/', Expert_view, name='Expert'),
    path('Regression/', Regression_view, name='Regression'),
]