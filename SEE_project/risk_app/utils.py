import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier, plot_tree


# Sensitivity Analysis
# model_func：替换为风险模型函数
def sensitivity_analysis(model_func, param_ranges, base_values, steps=20):
    results = []

    for param, (low, high) in param_ranges.items():
        values = np.linspace(low, high, steps)
        outputs = []

        for v in values:
            inputs = base_values.copy()
            inputs[param] = v
            result = model_func(**inputs)
            outputs.append(result)

        df = pd.DataFrame({
            param: values,
            'output': outputs
        })
        df['param_name'] = param
        results.append(df)

    return results  # list of DataFrames


# Decision Tree Modeling
def decision_tree_model(X, y):
    clf = DecisionTreeClassifier(max_depth=4, random_state=42)
    clf.fit(X, y)
    plt.figure(figsize=(36, 18))
    plot_tree(clf, feature_names=X.columns, class_names=np.unique(y).astype(str), filled=True)
    plt.title("Decision Tree for Risk Classification")
    plt.savefig('risk_app/picture/decision_tree.png')
    # plt.show()
    return clf


# Monte Carlo Simulation
def monte_carlo_simulation(model_func, param_dists, n_simulations=1000):
    outputs = []
    for _ in range(n_simulations):
        params = {key: dist() for key, dist in param_dists.items()}
        outputs.append(model_func(**params))
    return outputs


# Example risk model function
def example_risk_model(revenue, cost, probability_of_loss):
    margin = revenue - cost
    penalty = np.exp(probability_of_loss)  # 非线性风险影响
    adjusted_margin = np.log1p(max(margin, 0))  # 非线性利润调整
    risk_adjusted_return = adjusted_margin / penalty
    return risk_adjusted_return

# Visualization

# def plot_sensitivity(results):
#     plt.figure(figsize=(10, 6))
#     for param, (values, outputs) in results.items():
#         plt.plot(values, outputs, label=param)
#     plt.title("Sensitivity Analysis")
#     plt.xlabel("Parameter Value")
#     plt.ylabel("Output")
#     plt.legend()
#     plt.grid(True)
#     plt.savefig('picture/sensitivity.png')
#     plt.show()
def plot_sensitivity(results):
    n = len(results)
    fig, axs = plt.subplots(n, 1, figsize=(8, 4 * n))

    if n == 1:
        axs = [axs]

    for ax, df in zip(axs, results):
        param = df['param_name'].iloc[0]
        ax.plot(df[param], df['output'], marker='o')
        ax.set_xlabel(param)
        ax.set_ylabel("Model Output")
        ax.set_title(f"Sensitivity of Output to {param}")
        ax.grid(True)

    plt.tight_layout()
    plt.savefig('risk_app/picture/sensitivity.png')
    # plt.show()


def plot_monte_carlo(outputs):
    sns.histplot(outputs, kde=True, bins=30)
    plt.title("Monte Carlo Simulation Results")
    plt.xlabel("Simulated Output")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.savefig('risk_app/picture/monte_carlo.png')
    # plt.show()


# Example usage
if __name__ == '__main__':

    # 前端输入
    user_revenue = 1000
    user_cost = 500
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
