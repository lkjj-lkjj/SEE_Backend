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
        Task(3, 3, 7, 2), # 任务3：4-7时间需要1单位资源
        Task(4, 5, 9, 2)
    ]
    max_resource = 4  # 资源最大可用量

    # 执行资源均衡
    adjusted_tasks = resource_leveling(tasks, max_resource)
    print(adjusted_tasks)

    return JsonResponse({
        'code': 500,
        'msg': '1',
    })


@csrf_exempt
def smooth_view(request):
    # input_tasks = [
    #     # 关键任务（总时差=0，不可调整）
    #     {"id": 1, "duration": 5, "demand": 3, "es": 0, "ls": 0},  # 0-5
    #     {"id": 2, "duration": 5, "demand": 3, "es": 5, "ls": 5},  # 5-10
    #
    #     # 非关键任务（总时差>0，可调整）
    #     {"id": 3, "duration": 4, "demand": 2, "es": 0, "ls": 3},  # 总时差3（0→3）
    #     {"id": 4, "duration": 4, "demand": 2, "es": 2, "ls": 5}  # 总时差3（2→5）
    # ]
    # data = json.loads(request.body.decode('utf-8'))
    # print(data)
    # 执行资源平滑（保持总工期10不变）
    # adjusted_tasks = resource_smoothing(data, project_duration=10)
    # print("\n调整后优化进度：")
    # for t in adjusted_tasks:
    #     print(f"任务{t['id']} [时间: {t['start']}-{t['end']}, 需求: {t['demand']}, 总时差: {t['ls'] - t['es']}]")

    return JsonResponse({
        'code': 200,
        'msg': '1',
    })
