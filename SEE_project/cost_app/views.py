import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .alogrithm.Delphi_Method import DelphiCostEstimator
from .alogrithm.Expert_Judgment import estimate_project_cost


# Create your views here.
@csrf_exempt
def Delphi_view(request):
    data = json.loads(request.body.decode('utf-8'))
    function_points = data['function_points']
    modules_count = data['modules_count']
    interfaces_count = data['interfaces_count']
    technical_difficulty = data['technical_difficulty']
    team_experience = data['team_experience']
    expected_delivery_time = data['expected_delivery_time']
    # 创建估计器
    estimator = DelphiCostEstimator()
    # 添加专家（后台输入）
    estimator.add_expert("项目经理", 1.2)
    estimator.add_expert("技术负责人", 1.1)
    estimator.add_expert("资深开发", 1.0)
    estimator.add_expert("测试主管", 0.9)
    estimator.add_expert("业务分析师", 1.0)

    estimated_cost = estimator.estimate(
        function_points,
        modules_count,
        interfaces_count,
        technical_difficulty,
        team_experience,
        expected_delivery_time
    )
    return JsonResponse({
        'code': "200",
        'msg': estimated_cost
    })


@csrf_exempt
def Expert_view(request):
    data = json.loads(request.body.decode('utf-8'))
    function_points = data['function_points']
    modules_count = data['modules_count']
    interfaces_count = data['interfaces_count']
    technical_difficulty = data['technical_difficulty']
    team_experience = data['team_experience']
    expected_delivery_time = data['expected_delivery_time']
    estimated_cost = estimate_project_cost(
        function_points, modules_count, interfaces_count,
        technical_difficulty, team_experience, expected_delivery_time
    )
    return JsonResponse({
        'code': "200",
        'msg': estimated_cost
    })


@csrf_exempt
def Regression_view(request):
    return JsonResponse({'linear': 455731.75, 'ridge': 454773.54, 'lasso': 455731.67, 'random_forest': 214518.08,
                         'gradient_boosting': 179283.3})
