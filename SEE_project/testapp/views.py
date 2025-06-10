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

from .models import CountRecord


@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'code': 405, 'msg': '仅支持POST请求'}, status=405)

    try:
        # 1. 解析请求数据
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')

        # 2. 基础数据验证
        if not username or not password:
            raise ValidationError("用户名和密码不能为空")

        # 3. 用户认证（核心逻辑）
        user = authenticate(request, username=username, password=password)
        if not user:
            raise ValidationError("用户名或密码错误")

        # 4. 检查用户激活状态（若模型包含is_active字段）
        if hasattr(user, 'is_active') and not user.is_active:
            raise ValidationError("用户未激活，请联系管理员")

        # 6. 成功响应（返回敏感信息需谨慎）
        return JsonResponse({
            'code': 200,
            'msg': '登录成功',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'code': 400, 'msg': '无效的JSON数据'}, status=400)
    except ValidationError as e:
        return JsonResponse({'code': 401, 'msg': str(e)}, status=401)
    except Exception as e:
        # 生产环境应记录日志（如使用logging模块）
        return JsonResponse({
            'code': 500,
            'msg': '服务器内部错误',
            'error_detail': str(e) if request.user.is_superuser else '未知错误'
        }, status=500)


@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'], '仅支持POST请求')

    try:
        # 1. 解析请求数据
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        required_fields = ['username', 'password1', 'email']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"缺少必要字段: {field}")

        # 2. 数据验证
        username = data['username'].strip()
        password = data['password1'].strip()
        email = data['email'].strip()

        # if len(username) < 3 or len(username) > 20:
        #     raise ValidationError("用户名需在3-20字符之间")
        # if len(password) < 8:
        #     raise ValidationError("密码长度至少8位")
        # if '@' not in email or '.' not in email:
        #     raise ValidationError("邮箱格式不正确")

        # 3. 检查用户名唯一性
        if User.objects.filter(username=username).exists():
            raise ValidationError("用户名已存在")

        # 4. 密码加密（重要！）
        hashed_password = make_password(password)

        # 5. 创建用户并保存到数据库
        new_user = User(
            username=username,
            password=hashed_password,
            email=email
        )
        new_user.save()

        # 6. 成功响应
        return JsonResponse({
            'code': 200,
            'msg': '注册成功',
            'data': {'user_id': new_user.id}
        })

    except json.JSONDecodeError:
        return JsonResponse({'code': 400, 'msg': '无效的JSON数据'}, status=400)
    except ValidationError as e:
        return JsonResponse({'code': 400, 'msg': str(e)}, status=400)
    except Exception as e:
        # 记录详细错误日志（生产环境建议使用logging模块）
        return JsonResponse({
            'code': 500,
            'msg': '服务器内部错误',
            'error_detail': str(e) if settings.DEBUG else '未知错误'
        }, status=500)



# 测试存储EIcount
@csrf_exempt
def save_counts(request):
    if request.method == "POST":
        # 从 POST 请求中获取数据（根据前端传递方式调整）
        # 假设前端通过表单传递（form-data/x-www-form-urlencoded）
        data = json.loads(request.body.decode('utf-8'))
        ei_count = data['EIcount']
        eo_count = data['EOcount']
        print(ei_count, eo_count)

        # 校验数据（必填且为整数）
        if not ei_count or not eo_count:
            return JsonResponse({"code": 400, "msg": "EIcount 或 EOcount 为空"})
        try:
            ei = int(ei_count)
            eo = int(eo_count)
        except ValueError:
            return JsonResponse({"code": 400, "msg": "数值必须为整数"})

        # 创建并保存记录
        CountRecord.objects.create(EIcount=ei, EOcount=eo)
        return JsonResponse({"code": 200, "msg": "数据保存成功"})
    return JsonResponse({"code": 405, "msg": "仅支持 POST 请求"})


