from django.test import TestCase

# Create your tests here.
from datetime import datetime, timedelta


from datetime import datetime, timedelta
import numpy as np


def parse_date(date_str):
    """解析日期字符串为datetime对象"""
    return datetime.strptime(date_str, "%Y-%m-%d")


def resource_smoothing(tasks):
    """资源平滑算法实现"""
    # 解析日期并计算任务的时间窗口
    for task in tasks:
        task["es_date"] = parse_date(task["es"])
        task["ls_date"] = parse_date(task["ls"])
        task["start_window"] = (task["es_date"], task["ls_date"])
        task["end_date"] = task["es_date"] + timedelta(days=task["duration"])
        task["is_critical"] = (task["es"] == task["ls"])

    # 找出项目的开始和结束日期
    project_start = min(task["es_date"] for task in tasks)
    project_end = max(task["end_date"] for task in tasks)

    # 创建时间轴
    timeline = [(project_start + timedelta(days=i)) for i in range((project_end - project_start).days + 1)]

    # 初始化资源分配结果
    result_tasks = tasks.copy()

    # 计算资源需求曲线（初始状态）
    initial_resource_demand = calculate_resource_demand(result_tasks, timeline)

    # 按总时差排序非关键任务（从大到小）
    non_critical_tasks = [t for t in result_tasks if not t["is_critical"]]
    non_critical_tasks.sort(key=lambda x: (x["ls_date"] - x["es_date"]).days, reverse=True)

    # 为每个非关键任务寻找最优开始时间
    for task in non_critical_tasks:
        best_start_date = task["es_date"]
        min_variation = float('inf')

        # 在任务的时间窗口内尝试不同的开始时间
        current_date = task["es_date"]
        while current_date <= task["ls_date"]:
            # 临时修改任务开始时间
            original_start = task["es_date"]
            task["es_date"] = current_date
            task["end_date"] = current_date + timedelta(days=task["duration"])

            # 计算新的资源需求曲线
            new_resource_demand = calculate_resource_demand(result_tasks, timeline)
            variation = calculate_variation(new_resource_demand)

            # 更新最优解
            if variation < min_variation:
                min_variation = variation
                best_start_date = current_date

            # 恢复任务开始时间
            task["es_date"] = original_start
            task["end_date"] = original_start + timedelta(days=task["duration"])

            # 尝试下一个可能的开始时间（每天递增）
            current_date += timedelta(days=1)

        # 应用最优开始时间
        task["es_date"] = best_start_date
        task["end_date"] = best_start_date + timedelta(days=task["duration"])

    # 计算优化后的资源需求曲线
    optimized_resource_demand = calculate_resource_demand(result_tasks, timeline)

    # 格式化结果
    formatted_tasks = []
    for task in result_tasks:
        formatted_tasks.append({
            "id": task["id"],
            "duration": task["duration"],
            "demand": task["demand"],
            "es": task["es_date"].strftime("%Y-%m-%d"),
            "ls": task["ls"].strftime("%Y-%m-%d") if isinstance(task["ls"], datetime) else task["ls"],
            "is_critical": task["is_critical"]
        })

    return {
        "original_tasks": tasks,
        "optimized_tasks": formatted_tasks,
        "original_demand": initial_resource_demand,
        "optimized_demand": optimized_resource_demand,
        "timeline": timeline
    }


def calculate_resource_demand(tasks, timeline):
    """计算给定时间轴上的资源需求"""
    demand = [0] * len(timeline)
    for task in tasks:
        for i, date in enumerate(timeline):
            if task["es_date"] <= date < task["end_date"]:
                demand[i] += task["demand"]
    return demand


def calculate_variation(demand):
    """计算资源需求的波动程度（使用方差）"""
    return np.var(demand)


def print_results(results):
    """打印资源平滑结果"""
    print("\n===== 资源平滑结果 =====")

    print("\n原始任务安排:")
    for task in results["original_tasks"]:
        print(f"任务 {task['id']}: 持续时间={task['duration']}, 资源需求={task['demand']}, "
              f"最早开始={task['es']}, 最晚开始={task['ls']}, 关键={task['is_critical']}")

    print("\n优化后的任务安排:")
    for task in results["optimized_tasks"]:
        print(f"任务 {task['id']}: 持续时间={task['duration']}, 资源需求={task['demand']}, "
              f"开始时间={task['es']}, 最晚开始={task['ls']}, 关键={task['is_critical']}")

    print("\n资源需求统计:")
    print(f"原始资源需求方差: {calculate_variation(results['original_demand']):.2f}")
    print(f"优化后资源需求方差: {calculate_variation(results['optimized_demand']):.2f}")
    print(
        f"资源需求方差减少: {calculate_variation(results['original_demand']) - calculate_variation(results['optimized_demand']):.2f}")

    # 打印资源需求曲线
    print("\n资源需求曲线:")
    dates = [date.strftime("%Y-%m-%d") for date in results["timeline"]]
    for i, date in enumerate(dates):
        print(f"{date}: 原始需求={results['original_demand'][i]}, 优化后需求={results['optimized_demand'][i]}")


# 主函数
def main():
    input_tasks = [
        # 关键任务（总时差=0，不可调整）
        {"id": 1, "duration": 5, "demand": 3, "es": "2025-06-11", "ls": "2025-06-11"},
        {"id": 2, "duration": 5, "demand": 3, "es": "2025-06-16", "ls": "2025-06-16"},

        # 非关键任务（总时差>0，可调整）
        {"id": 3, "duration": 4, "demand": 2, "es": "2025-06-11", "ls": "2025-06-14"},
        {"id": 4, "duration": 4, "demand": 2, "es": "2025-06-13", "ls": "2025-06-16"}
    ]

    results = resource_smoothing(input_tasks)
    print_results(results)


if __name__ == "__main__":
    main()

