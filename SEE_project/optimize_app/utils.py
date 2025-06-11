# Resource Leveling：通过调整任务的开始和结束时间，解决资源过度分配（如资源冲突或超负荷）的问题，确保资源使用不超过可用限制
# Resource Smoothing：在不改变项目总工期的前提下，调整非关键路径任务的资源分配，使资源需求波动最小化

class Task:
    def __init__(self, task_id, start_time, end_time, resource_demand):
        self.task_id = task_id
        self.original_start = start_time  # 原始开始时间
        self.original_end = end_time  # 原始结束时间
        self.start = start_time  # 调整后开始时间
        self.end = end_time  # 调整后结束时间
        self.resource_demand = resource_demand  # 资源需求量（单位：人/小时）

    def __repr__(self):
        return f"Task {self.task_id} [时间: {self.start}-{self.end}, 资源需求: {self.resource_demand}]"


def check_resource_conflict(tasks, max_resource):
    """检查当前任务列表是否存在资源冲突"""
    timeline = {}
    # 收集所有时间点并排序
    time_points = sorted(set([t.start for t in tasks] + [t.end for t in tasks]))

    for i in range(len(time_points) - 1):
        current_start = time_points[i]
        current_end = time_points[i + 1]
        # 计算当前时间段内的资源使用总量
        total_usage = sum(
            t.resource_demand
            for t in tasks
            if t.start <= current_start and t.end >= current_end
        )
        if total_usage > max_resource:
            return (current_start, current_end, total_usage)
    return None


def resource_leveling(tasks, max_resource):
    """资源均衡主函数（贪心调整策略）"""
    # 按原始开始时间排序任务（可根据实际需求调整排序策略）
    sorted_tasks = sorted(tasks, key=lambda t: t.original_start)
    adjusted_tasks = []

    for task in sorted_tasks:
        # 初始使用原始时间
        candidate_start = task.original_start
        candidate_end = task.original_end

        while True:
            # 创建临时任务列表检查冲突
            temp_tasks = adjusted_tasks + [Task(
                task.task_id, candidate_start, candidate_end, task.resource_demand
            )]

            conflict = check_resource_conflict(temp_tasks, max_resource)
            if not conflict:
                break  # 无冲突，确定当前时间

            # 存在冲突时，将任务开始时间后移1单位时间（可根据需求调整步长）
            candidate_start += 1
            candidate_end += 1

            # 防止无限循环（实际应用中应添加最大调整次数限制）
            if candidate_start > 100:
                raise ValueError(f"任务{task.task_id}无法找到可用时间窗口")

        # 更新任务时间
        task.start = candidate_start
        task.end = candidate_end
        adjusted_tasks.append(task)

    return adjusted_tasks


# 示例演示
# if __name__ == "__main__":
#     # 初始任务列表（假设资源限制为2单位）
#     tasks = [
#         Task(1, 0, 3, 2),  # 任务1：0-3时间需要1单位资源
#         Task(2, 2, 5, 3),  # 任务2：2-5时间需要1单位资源
#         Task(3, 4, 7, 2)  # 任务3：4-7时间需要1单位资源
#     ]
#     max_resource = 4  # 资源最大可用量
#
#     print("调整前原始任务：")
#     for t in tasks:
#         print(t)
#
#     # 执行资源均衡
#     adjusted_tasks = resource_leveling(tasks, max_resource)
#
#     print("\n调整后任务：")
#     for t in adjusted_tasks:
#         print(t)
#
#     # 验证最终资源使用情况
#     print("\n最终资源使用验证：")
#     conflict = check_resource_conflict(adjusted_tasks, max_resource)
#     if not conflict:
#         print("所有时间段资源使用均未超过限制")
#     else:
#         print(f"发现冲突：时间段 {conflict[0]}-{conflict[1]}，资源使用量 {conflict[2]}")


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

    # 计算项目总工期
    project_duration = (project_end - project_start).days

    print(f"项目总工期: {project_duration} 天")

    # 创建时间轴
    timeline = [(project_start + timedelta(days=i)) for i in range(project_duration + 1)]

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

            # 检查是否违反项目总工期约束
            new_project_end = max(t["end_date"] for t in result_tasks)
            new_project_duration = (new_project_end - project_start).days

            if new_project_duration <= project_duration:
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

    # 验证优化后的项目总工期
    optimized_project_end = max(t["end_date"] for t in result_tasks)
    optimized_project_duration = (optimized_project_end - project_start).days

    print(f"优化后的项目总工期: {optimized_project_duration} 天")

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
        "timeline": timeline,
        "project_duration": project_duration,
        "optimized_project_duration": optimized_project_duration
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

    print(f"\n项目总工期: {results['project_duration']} 天")
    print(f"优化后的项目总工期: {results['optimized_project_duration']} 天")

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


if __name__ == "__main__":
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
