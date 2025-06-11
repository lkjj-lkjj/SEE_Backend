import numpy as np
import pandas as pd
from typing import List


class DelphiCostEstimator:
    """基于Delphi Method的项目成本估计器"""

    def __init__(self):
        self.experts = []
        self.estimations = []
        self.consensus_threshold = 0.1  # 共识阈值，当估计值的标准差与均值的比例小于此值时认为达成共识
        self.max_rounds = 5  # 最大迭代轮数

    def add_expert(self, name: str, weight: float = 1.0):
        """添加专家及其权重"""
        self.experts.append({"name": name, "weight": weight})

    def estimate(self,
                 function_points: int,
                 modules_count: int,
                 interfaces_count: int,
                 technical_difficulty: float,
                 team_experience: float,
                 expected_delivery_time: float) -> float:
        """使用Delphi方法估计项目成本"""

        # 输入验证
        self._validate_inputs(
            function_points,
            modules_count,
            interfaces_count,
            technical_difficulty,
            team_experience,
            expected_delivery_time
        )

        # 初始估计值
        initial_estimates = self._get_initial_estimates(
            function_points,
            modules_count,
            interfaces_count,
            technical_difficulty,
            team_experience,
            expected_delivery_time
        )

        # 多轮Delphi过程
        current_estimates = initial_estimates
        round_num = 1

        while not self._check_consensus(current_estimates) and round_num <= self.max_rounds:
            # 获取反馈并调整估计
            current_estimates = self._adjust_estimates(current_estimates, round_num)
            round_num += 1

        # 计算最终共识估计值
        final_estimate = self._calculate_final_estimate(current_estimates)

        return final_estimate

    def _validate_inputs(self,
                         function_points: int,
                         modules_count: int,
                         interfaces_count: int,
                         technical_difficulty: float,
                         team_experience: float,
                         expected_delivery_time: float):

        # 验证输入范围
        if not all(arg > 0 for arg in (function_points, modules_count, interfaces_count, expected_delivery_time)):
            raise ValueError("功能点数、模块数、接口数和交付时间必须大于0")

        if not (1.0 <= technical_difficulty <= 5.0):
            raise ValueError("技术难度系数必须在1.0-5.0之间")

        if not (1.0 <= team_experience <= 5.0):
            raise ValueError("团队经验值必须在1.0-5.0之间")

    def _get_initial_estimates(self,
                               function_points: int,
                               modules_count: int,
                               interfaces_count: int,
                               technical_difficulty: float,
                               team_experience: float,
                               expected_delivery_time: float) -> List[float]:
        """获取初始估计值"""
        # 这里使用简化的公式计算初始估计值
        # 实际应用中可以使用更复杂的模型或专家判断
        base_cost = function_points * 1000  # 假设每个功能点的基础成本为1000元
        module_factor = modules_count * 0.1  # 模块数量影响因子
        interface_factor = interfaces_count * 0.05  # 接口数量影响因子

        # 计算初始估计值
        initial_estimates = []
        for expert in self.experts:
            # 每个专家可能有不同的观点，通过随机扰动模拟
            random_factor = np.random.normal(1.0, 0.15)  # 随机因子，均值为1，标准差为0.15
            cost = (base_cost * (1 + module_factor + interface_factor) *
                    technical_difficulty / team_experience *
                    (12 / expected_delivery_time)) * random_factor * expert["weight"]
            initial_estimates.append(cost)

        return initial_estimates

    def _check_consensus(self, estimates: List[float]) -> bool:
        """检查是否达成共识"""
        if len(estimates) < 2:
            return True

        mean_estimate = np.mean(estimates)
        std_dev = np.std(estimates)
        cv = std_dev / mean_estimate if mean_estimate > 0 else float('inf')

        return cv < self.consensus_threshold

    def _adjust_estimates(self, current_estimates: List[float], round_num: int) -> List[float]:
        """根据反馈调整估计值"""
        # 计算当前估计的统计信息
        mean_estimate = np.mean(current_estimates)
        median_estimate = np.median(current_estimates)
        std_dev = np.std(current_estimates)

        # 记录当前轮次的估计
        self.estimations.append({
            "round": round_num,
            "estimates": current_estimates.copy(),
            "mean": mean_estimate,
            "median": median_estimate,
            "std_dev": std_dev
        })

        # 打印当前轮次的估计统计信息
        print(f"\n第{round_num}轮估计:")
        print(f"平均估计值: {mean_estimate:.2f}")
        print(f"中位数估计值: {median_estimate:.2f}")
        print(f"标准差: {std_dev:.2f}")
        print(f"变异系数: {std_dev / mean_estimate:.2f}")

        # 调整估计值 - 模拟专家根据反馈调整估计
        adjusted_estimates = []
        for i, estimate in enumerate(current_estimates):
            # 向均值方向调整，但保留一定的专家独立性
            adjustment_factor = np.random.normal(0.7, 0.2)  # 调整因子，均值为0.7，标准差为0.2
            adjusted_estimate = estimate + (mean_estimate - estimate) * adjustment_factor
            adjusted_estimates.append(adjusted_estimate)

        return adjusted_estimates

    def _calculate_final_estimate(self, estimates: List[float]) -> float:
        """计算最终共识估计值"""
        # 记录最后一轮的估计
        round_num = len(self.estimations) + 1
        mean_estimate = np.mean(estimates)
        median_estimate = np.median(estimates)
        std_dev = np.std(estimates)

        self.estimations.append({
            "round": round_num,
            "estimates": estimates.copy(),
            "mean": mean_estimate,
            "median": median_estimate,
            "std_dev": std_dev
        })

        print(f"\n最终估计结果:")
        print(f"平均估计值: {mean_estimate:.2f}")
        print(f"中位数估计值: {median_estimate:.2f}")
        print(f"标准差: {std_dev:.2f}")
        print(f"变异系数: {std_dev / mean_estimate:.2f}")

        # 返回加权平均值作为最终估计
        return mean_estimate

    def get_estimation_history(self) -> pd.DataFrame:
        """获取估计历史记录"""
        if not self.estimations:
            return pd.DataFrame()

        # 转换估计历史为DataFrame
        history_data = []
        for est in self.estimations:
            for i, expert_est in enumerate(est["estimates"]):
                history_data.append({
                    "round": est["round"],
                    "expert": self.experts[i]["name"],
                    "estimate": round(expert_est, 2),
                    "mean": round(est["mean"], 2),
                    "median": round(est["median"], 2),
                    "std_dev": round(est["std_dev"], 2)
                })

        return pd.DataFrame(history_data)



if __name__ == "__main__":
    # 示例

    # 创建估计器
    estimator = DelphiCostEstimator()
    # 添加专家（后台输入）
    estimator.add_expert("项目经理", 1.2)
    estimator.add_expert("技术负责人", 1.1)
    estimator.add_expert("资深开发", 1.0)
    estimator.add_expert("测试主管", 0.9)
    estimator.add_expert("业务分析师", 1.0)

    # 用户输入
    function_points = 100
    modules_count = 5
    interfaces_count = 20
    technical_difficulty = 3
    team_experience = 4
    expected_delivery_time = 6

    estimated_cost = estimator.estimate(
        function_points,
        modules_count,
        interfaces_count,
        technical_difficulty,
        team_experience,
        expected_delivery_time
    )

    # 显示结果
    print(f"\n最终估计项目成本: {estimated_cost:.2f}元")

    # 显示估计历史
    history = estimator.get_estimation_history()
    if not history.empty:
        print("\n估计历史:")
        print(history)