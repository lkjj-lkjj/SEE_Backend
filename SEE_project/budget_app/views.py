# Create your views here.
import json

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
    ROI = calculate_roi(initial_investment, sum(cash_flow))
    npv = calculate_npv(discount_rate, cash_flow, initial_investment)
    irr = calculate_irr([- initial_investment] + cash_flow)
    pbp = calculate_payback_period(cash_flow, initial_investment, discount_rate)
    return JsonResponse({
        'code': '1',
        'data': {
            'ROI': ROI,
            "npv": npv,
            'irr': irr,
            'pbp': pbp
        }
    })


# 预测功能
@csrf_exempt
def forecast_view(request):
    return JsonResponse()
