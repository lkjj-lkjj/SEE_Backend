# Expert Judgment

import numpy as np

def estimate_project_cost(
        function_points,
        modules_count,
        interfaces_count,
        technical_difficulty,
        team_experience,
        expected_delivery_time
):
    """
    使用Expert Judgment算法估算项目成本

    参数:
    function_points: 功能点数
    modules_count: 模块数
    interfaces_count: 接口数
    technical_difficulty: 技术难度系数 (1-5, 5表示最高难度)
    team_experience: 团队经验值 (1-5, 5表示最高经验)
    expected_delivery_time: 期望交付时间(月)

    返回:
    estimated_cost: 估计的项目成本
    """

    # 基本参数权重 - 这些权重可以根据历史数据或专家经验调整
    weights = {
        'function_points': 0.4,
        'modules_count': 0.2,
        'interfaces_count': 0.15,
        'technical_difficulty': 0.15,
        'team_experience': 0.1,
        'expected_delivery_time': 0.1
    }

    # 基础成本计算 - 可以根据组织的历史项目数据调整
    base_cost = 50000  # 基础成本，单位：元

    # 验证输入范围
    if not all(arg > 0 for arg in (function_points, modules_count, interfaces_count, expected_delivery_time)):
        raise ValueError("功能点数、模块数、接口数和交付时间必须大于0")

    if not (1.0 <= technical_difficulty <= 5.0):
        raise ValueError("技术难度系数必须在1.0-10.0之间")

    if not (1.0 <= team_experience <= 5.0):
        raise ValueError("团队经验值必须在1.0-10.0之间")


    # 计算各个因素的影响
    function_points_factor = function_points * 1000 * weights['function_points']
    modules_factor = modules_count * 5000 * weights['modules_count']
    interfaces_factor = interfaces_count * 3000 * weights['interfaces_count']

    # 技术难度调整系数 (技术难度越高，成本越高)
    difficulty_factor = (technical_difficulty / 5) * 20000 * weights['technical_difficulty']

    # 团队经验调整系数 (经验越高，成本越低)
    experience_factor = ((5 - team_experience) / 5) * 15000 * weights['team_experience']

    # 时间压力调整系数 (时间越短，成本越高)
    # 假设标准交付时间为12个月，每减少1个月增加5%的成本
    standard_time = 12
    time_pressure_factor = max(0, (standard_time - expected_delivery_time) / standard_time) * 30000 * weights[
        'expected_delivery_time']

    # 计算总成本
    estimated_cost = (base_cost +
                      function_points_factor +
                      modules_factor +
                      interfaces_factor +
                      difficulty_factor +
                      experience_factor +
                      time_pressure_factor)

    # 应用随机波动 (模拟不确定性)
    uncertainty_factor = np.random.normal(1, 0.1)  # 平均值1，标准差0.1的正态分布
    estimated_cost *= uncertainty_factor



    return round(estimated_cost,2)  # 单位：元


if __name__ == '__main__':
    # 示例

    function_points = 100
    modules_count = 5
    interfaces_count = 20
    technical_difficulty = 3
    team_experience = 4
    expected_delivery_time = 6

    estimated_cost = estimate_project_cost(
        function_points, modules_count, interfaces_count,
        technical_difficulty, team_experience, expected_delivery_time
    )

    print(f"\n项目估计成本: ¥{estimated_cost:,.2f}")

    # 提供置信区间
    lower_bound = estimated_cost * 0.85  # 85%置信下限
    upper_bound = estimated_cost * 1.15  # 85%置信上限
    print(f"置信区间(85%): ¥{lower_bound:,.2f} - ¥{upper_bound:,.2f}")