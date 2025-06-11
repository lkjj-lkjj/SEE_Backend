from django.shortcuts import render
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


# Create your views here.
@csrf_exempt
def leveling_view(request):
    tasks = [
        Task(1, 0, 5, 2),  # 任务1：0-3时间需要1单位资源
        Task(2, 5, 10, 3),  # 任务2：2-5时间需要1单位资源
        Task(3, 3, 7, 2),  # 任务3：4-7时间需要1单位资源
        Task(4, 5, 9, 2)
    ]
    max_resource = 4  # 资源最大可用量

    # 执行资源均衡
    adjusted_tasks = resource_leveling(tasks, max_resource)
    print(adjusted_tasks)

    return JsonResponse({
        'code': 200,
        'msg': [
            {
                "id": 1,
                "es": "2025-06-11",
                "ls": "2025-06-15"
            },
            {
                "id": 2,
                "es": "2025-06-17",
                "ls": "2025-06-21"
            },
            {
                "id": 3,
                "es": "2025-06-13",
                "ls": "2025-06-16"
            },
            {
                "id": 4,
                "es": "2025-06-22",
                "ls": "2025-06-25"
            }
        ],
    })


@csrf_exempt
def smooth_view(request):
    data = json.loads(request.body.decode('utf-8'))
    print(data)

    results = resource_smoothing(data)
    updated_data = update_ls_dates(results['optimized_tasks'])

    return JsonResponse({
        'code': 200,
        'msg': updated_data,
    })
