import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import *


# Create your views here.
@csrf_exempt
def pic_view(request):
    # 前端输入
    data = json.loads(request.body.decode('utf-8'))
    user_revenue = data['user_revenue']
    user_cost = data['user_cost']
    # ----------------------------------------------------------
    # 敏感性分析（sensitivity_analysis）
    base_values = {
        'revenue': user_revenue,
        'cost': user_cost,
        'probability_of_loss': 0.2
    }
    user_revenue_high = user_revenue + user_revenue * 0.2
    user_revenue_low = user_revenue - user_revenue * 0.2
    user_cost_high = user_cost + user_cost * 0.2
    user_cost_low = user_cost - user_cost * 0.2

    param_ranges = {
        'revenue': (user_revenue_low, user_revenue_high),
        'cost': (user_cost_low, user_cost_high),
        'probability_of_loss': (0.1, 0.5)
    }
    sensitivity_results = sensitivity_analysis(example_risk_model, param_ranges, base_values)
    plot_sensitivity(sensitivity_results)
    # ----------------------------------------------------------
    user_revenue_std = user_revenue * np.random.uniform(0.05, 0.15)
    user_cost_std = user_cost * np.random.uniform(0.05, 0.3)
    # ----------------------------------------------------------
    # 蒙特卡洛模拟
    param_dists = {
        'revenue': lambda: np.random.normal(user_revenue, user_revenue_std),
        'cost': lambda: np.random.normal(user_cost, user_cost_std),
        'probability_of_loss': lambda: np.clip(np.random.beta(2, 5), 0, 1)
    }
    mc_outputs = monte_carlo_simulation(example_risk_model, param_dists)
    plot_monte_carlo(mc_outputs)
    # ----------------------------------------------------------
    # 决策树
    data = pd.DataFrame({
        'revenue': np.random.normal(user_revenue, user_revenue_std, 100),
        'cost': np.random.normal(user_cost, user_cost_std, 100),
        'probability_of_loss': np.clip(np.random.beta(2, 5, 100), 0, 1)
    })
    data['risk_score'] = data.apply(
        lambda row: example_risk_model(row['revenue'], row['cost'], row['probability_of_loss']), axis=1)
    data['risk_level'] = pd.qcut(data['risk_score'], q=3, labels=['Low', 'Medium', 'High'])
    decision_tree_model(data[['revenue', 'cost', 'probability_of_loss']], data['risk_level'])

    # 返回图片url
    current_dir = os.path.dirname(os.path.abspath(__file__))
    picture_dir = os.path.join(current_dir, 'picture')
    print(picture_dir)
    picture_urls = []

    # 检查目录是否存在
    if os.path.exists(picture_dir):
        # 遍历目录中的图片文件
        for filename in os.listdir(picture_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                # 构建完整的图片URL
                picture_url = 'static/' + f"picture/{filename}"
                print('test', picture_url)
                picture_urls.append(picture_url)
    else:
        print('no info')
    print(picture_urls)
    return JsonResponse({
        'code': '200',
        'msg': picture_urls
    })
