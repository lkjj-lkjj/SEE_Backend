from django.shortcuts import render

# Create your views here.
import json

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import *

# 计算模块
@csrf_exempt
def calculate_view(request):
    data = json.loads(request.body.decode('utf-8'))
    print(data)
    initial_investment = data['initial_investment']
    discount_rate = data['discount_rate']
    cash_flow = [item['return'] for item in data['annual_returns']]
    print(initial_investment,sum(cash_flow))
    ROI = calculate_roi(initial_investment,sum(cash_flow))
    npv = calculate_npv(discount_rate,cash_flow,initial_investment)
    irr = calculate_irr([- initial_investment]+cash_flow)
    pbp = calculate_payback_period(cash_flow,initial_investment,discount_rate)
    print(ROI,npv,irr,pbp)
    return JsonResponse({
        'code':'1',
        'data':{
            'ROI':ROI,
            "npv":npv,
            'irr':irr,
            'pbp':pbp
        }
    })

# 预测功能
@csrf_exempt
def forecast_view(request):

    return JsonResponse()