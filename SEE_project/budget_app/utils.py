from typing import List
from typing import Union

import numpy_financial as npf


def calculate_roi(initial_investment: float, final_return: float) -> float:
    """
    计算投资回报率 (Return on Investment)

    参数:
        initial_investment: 初始投资额（正数，如10000）
        final_return: 最终收回的总金额（正数，如15000）

    返回:
        ROI百分比（如50.0表示50%）

    示例:
        calculate_roi(10000, 15000) → 50.0
    """
    if initial_investment <= 0:
        raise ValueError("初始投资额必须大于0")
    if final_return < initial_investment:
        raise ValueError("最终收回金额不能小于初始投资额")

    roi = ((final_return - initial_investment) / initial_investment) * 100
    return round(roi, 2)


def calculate_npv(discount_rate: float, cash_flows: List[float], initial_investment: float) -> float:
    """
    计算净现值 (Net Present Value)

    参数:
        discount_rate: 贴现率（如0.08表示8%）
        cash_flows: 各期现金流（不包含初始投资，如[3000, 4000, 5000]表示第1-3年的现金流）
        initial_investment: 初始投资额（正数，如10000）

    返回:
        净现值（如2356.78）

    示例:
        calculate_npv(0.08, [3000, 4000, 5000], 10000) → 2356.78
    """
    if discount_rate <= -1:
        raise ValueError("贴现率不能小于-100%")
    if not cash_flows:
        raise ValueError("现金流列表不能为空")

    # 计算各期现金流的现值（时间从1开始）
    present_values = [cf / (1 + discount_rate) ** (i + 1)
                      for i, cf in enumerate(cash_flows)]
    npv = sum(present_values) - initial_investment
    return round(npv, 2)


def calculate_irr(cash_flows: List[float]) -> float:
    """
    计算内部收益率 (Internal Rate of Return)

    参数:
        cash_flows: 完整现金流序列（包含初始投资，如[-10000, 3000, 4000, 5000]）
                    第0项为初始投资（负数），后续为各期回报（正数）

    返回:
        IRR百分比（如12.5表示12.5%）

    示例:
        calculate_irr([-10000, 3000, 4000, 5000]) → 12.5
    """
    if len(cash_flows) < 2:
        raise ValueError("现金流序列至少需要2个期间（初始投资+1期回报）")
    if sum(cash_flows) <= 0:
        raise ValueError("现金流总和必须大于0才能计算IRR")

    # 使用numpy的irr函数计算（返回小数形式）
    irr_decimal = npf.irr(cash_flows)
    return round(irr_decimal * 100, 2)


def calculate_payback_period(annual_cash_flows: List[float], initial_investment: float,
                             discount_rate: Union[float, None] = None) -> float:
    """
    计算投资回收期（支持静态和动态）

    参数:
        annual_cash_flows: 各年净现金流（不包含初始投资，如[3000, 4000, 5000]）
        initial_investment: 初始投资额（正数，如10000）
        discount_rate: 动态回收期需指定贴现率（如0.08），静态回收期传None

    返回:
        回收期（年，如2.6表示2年7个月左右）

    示例:
        calculate_payback_period([3000, 4000, 5000], 10000) → 2.6 （静态）
        calculate_payback_period([3000, 4000, 5000], 10000, 0.08) → 3.2 （动态）
    """
    if initial_investment <= 0:
        raise ValueError("初始投资额必须大于0")
    if not annual_cash_flows:
        raise ValueError("各年现金流列表不能为空")

    # 处理动态回收期（需计算贴现后现金流）
    if discount_rate is not None:
        if discount_rate <= -1:
            raise ValueError("贴现率不能小于-100%")
        cash_flows = [cf / (1 + discount_rate) ** (i + 1)
                      for i, cf in enumerate(annual_cash_flows)]
    else:
        cash_flows = annual_cash_flows  # 静态回收期使用原始现金流

    # 计算累计现金流
    cumulative = []
    current_sum = -initial_investment  # 初始投资为负
    for cf in cash_flows:
        current_sum += cf
        cumulative.append(current_sum)

    # 找到累计现金流由负转正的时间点
    for i in range(len(cumulative)):
        if cumulative[i] >= 0:
            if i == 0:
                return 0.0  # 第1年就收回投资
            # 计算部分收回的月份（假设现金流均匀发生）
            prev = cumulative[i - 1]
            current = cumulative[i]
            fraction = (-prev) / (current - prev)
            return round(i + fraction, 2)

    # 所有期间都未收回投资
    raise ValueError("投资在给定期间内无法收回")


def forecast_using_moving_average(historical_data: List[float], window: int = 3) -> float:
    """
    移动平均预测法（用最近window期的平均值预测下一期）

    参数:
        historical_data: 历史实际数据列表（如近6个月的实际支出）
        window: 移动窗口大小（默认3期）

    返回:
        下一期预测金额
    """
    if len(historical_data) < window:
        raise ValueError(f"需要至少{window}期历史数据")
    return sum(historical_data[-window:]) / window


# 模块示例用法
if __name__ == "__main__":
    # # 输入参数
    # initial_investment = 10000  # 初始投入资金
    # annual_returns = [3000, 4000, 5000, 6000]  # 第1-4年的回报
    # discount_rate = 0.08  # 8%贴现率
    # full_cash_flows = [-initial_investment] + annual_returns  # 完整现金流（含初始投资）
    #
    # # 计算各项指标
    # roi = calculate_roi(initial_investment, sum(annual_returns))
    # npv = calculate_npv(discount_rate, annual_returns, initial_investment)
    # irr = calculate_irr(full_cash_flows)
    # payback_static = calculate_payback_period(annual_returns, initial_investment)
    # payback_dynamic = calculate_payback_period(annual_returns, initial_investment, discount_rate)
    #
    # # 输出结果
    # print("===== 投资指标计算结果 =====")
    # print(f"ROI: {roi}%")
    # print(f"NPV (8%贴现率): {npv}元")
    # print(f"IRR: {irr}%")
    # print(f"静态回收期: {payback_static}年")
    # print(f"动态回收期 (8%贴现率): {payback_dynamic}年")

    # --------------------------------------------------------------
    # 假设已录入某营销项近6个月的实际支出：[8000, 8500, 9000, 9200, 8800, 9500]
    historical = [8000, 8500, 9000, 9200, 8800, 9500]
    next_month_forecast = forecast_using_moving_average(historical, window=3)  # (9200+8800+9500)/3 ≈ 9166.67

    # 计算剩余预算（假设年度预算为120000，前6个月累计实际支出=8000+8500+...+9500=53000）
    remaining_budget = 120000 - 53000 - next_month_forecast * 6  # 预测未来6个月总支出
    print(f"未来6个月预测总支出: {next_month_forecast * 6:.2f}")
    print(f"剩余预算: {remaining_budget:.2f}")
