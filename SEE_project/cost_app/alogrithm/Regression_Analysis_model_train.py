import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from typing import Dict, Tuple
import os
import joblib


class RegressionCostEstimator:
    """基于回归算法的项目成本估计器"""

    def __init__(self, model_type):
        """
        初始化回归估计器

        参数:
            model_type: 回归模型类型，可选值: 'linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.features = [
            "function_points", "modules_count", "interfaces_count",
            "technical_difficulty", "team_experience", "expected_delivery_time"
        ]

        # 初始化模型
        self._initialize_model()

    def _initialize_model(self):
        """根据模型类型初始化回归模型"""
        if self.model_type == "linear":
            self.model = LinearRegression()
        elif self.model_type == "ridge":
            self.model = Ridge(alpha=1.0)
        elif self.model_type == "lasso":
            self.model = Lasso(alpha=0.1)
        elif self.model_type == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif self.model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")

        # 创建包含标准化和模型的管道
        self.pipeline = Pipeline([
            ('scaler', self.scaler),
            ('regressor', self.model)
        ])

    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42):
        """
        训练回归模型

        参数:
            X: 特征数据，包含功能点数、模块数等
            y: 目标数据，项目成本
            test_size: 测试集比例
            random_state: 随机种子
        """
        # 分割训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # 训练模型
        self.pipeline.fit(X_train, y_train)



        # 在测试集上评估模型
        y_pred = self.pipeline.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)

        print(f"模型评估结果:")
        print(f"均方误差 (MSE): {mse:.2f}")
        print(f"均方根误差 (RMSE): {rmse:.2f}")
        print(f"决定系数 (R²): {r2:.4f}")

        return {
            "mse": mse,
            "rmse": rmse,
            "r2": r2
        }

    def save_model(self, filepath: str):
        """
        保存训练好的模型到文件

        参数:
            filepath: 模型保存路径
        """
        # 确保目录存在
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # 保存模型
        joblib.dump(self.pipeline, filepath)
        print(f"模型已保存到: {filepath}")

    def load_model(self, filepath: str):
        """
        从文件加载已训练的模型

        参数:
            filepath: 模型文件路径
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"模型文件不存在: {filepath}")

        # 加载模型
        self.pipeline = joblib.load(filepath)
        print(f"已从 {filepath} 加载模型")

        # 更新模型类型和模型实例
        self.model = self.pipeline.named_steps['regressor']
        self.model_type = type(self.model).__name__.lower()
        if 'randomforest' in self.model_type:
            self.model_type = 'random_forest'
        elif 'gradientboosting' in self.model_type:
            self.model_type = 'gradient_boosting'
        elif 'linear' in self.model_type:
            self.model_type = 'linear'
        elif 'ridge' in self.model_type:
            self.model_type = 'ridge'
        elif 'lasso' in self.model_type:
            self.model_type = 'lasso'

    def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5):
        """
        使用交叉验证评估模型

        参数:
            X: 特征数据
            y: 目标数据
            cv: 交叉验证折数
        """
        scores = cross_val_score(self.pipeline, X, y, cv=cv, scoring='neg_mean_squared_error')
        rmse_scores = np.sqrt(-scores)

        print(f"交叉验证结果 ({cv}折):")
        print(f"RMSE: {rmse_scores}")
        print(f"平均RMSE: {np.mean(rmse_scores):.2f} ± {np.std(rmse_scores):.2f}")

        return {
            "rmse_scores": rmse_scores,
            "mean_rmse": np.mean(rmse_scores),
            "std_rmse": np.std(rmse_scores)
        }

    def predict(self, features: Dict) -> float:
        """
        预测项目成本

        参数:
            features: 包含所有必要特征的字典

        返回:
            预测的项目成本
        """
        # 验证输入特征
        self._validate_features(features)

        # 准备输入数据
        input_data = np.array([
            features["function_points"],
            features["modules_count"],
            features["interfaces_count"],
            features["technical_difficulty"],
            features["team_experience"],
            features["expected_delivery_time"]
        ]).reshape(1, -1)

        # 预测成本
        predicted_cost = self.pipeline.predict(input_data)[0]

        return predicted_cost

    def _validate_features(self, features: Dict):
        """验证输入特征的有效性"""
        required_features = self.features

        for feature in required_features:
            if feature not in features:
                raise ValueError(f"缺少必要特征: {feature}")

        # 验证功能点数
        if features["function_points"] <= 0:
            raise ValueError("功能点数必须大于0")

        # 验证模块数
        if features["modules_count"] <= 0:
            raise ValueError("模块数必须大于0")

        # 验证接口数
        if features["interfaces_count"] < 0:
            raise ValueError("接口数不能为负数")

        # 验证技术难度系数
        if features["technical_difficulty"] < 1.0 or features["technical_difficulty"] > 5.0:
            raise ValueError("技术难度系数应在1到5之间")

        # 验证团队经验值
        if features["team_experience"] < 1.0 or features["team_experience"] > 5.0:
            raise ValueError("团队经验值应在1到5之间")

        # 验证期望交付时间
        if features["expected_delivery_time"] <= 0:
            raise ValueError("期望交付时间必须大于0")

    def feature_importance(self, X: pd.DataFrame = None):
        """
        获取特征重要性（仅适用于支持特征重要性的模型）

        参数:
            X: 特征数据，用于获取特征名称

        返回:
            特征重要性字典
        """
        if X is None and hasattr(self.model, 'feature_importances_'):
            # 如果没有提供X，使用默认特征名称
            feature_names = self.features
            importances = self.model.feature_importances_
        elif hasattr(self.model, 'feature_importances_'):
            # 使用X的列名作为特征名称
            feature_names = X.columns
            importances = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            # 线性模型使用系数作为重要性
            feature_names = self.features if X is None else X.columns
            importances = np.abs(self.model.coef_)
        else:
            raise ValueError("该模型不支持特征重要性分析")

        # 创建特征重要性字典
        importance_dict = {name: importance for name, importance in zip(feature_names, importances)}

        # 排序
        sorted_importance = {k: v for k, v in sorted(importance_dict.items(), key=lambda item: item[1], reverse=True)}

        return sorted_importance


def create_sample_data(n_samples: int = 100, random_state: int = 42) -> Tuple[pd.DataFrame, pd.Series]:
    """
    创建示例数据集用于训练和测试

    参数:
        n_samples: 样本数量
        random_state: 随机种子

    返回:
        X: 特征数据
        y: 目标数据
    """
    np.random.seed(random_state)

    # 生成特征数据
    function_points = np.random.randint(10, 200, n_samples)
    modules_count = np.random.randint(1, 20, n_samples)
    interfaces_count = np.random.randint(0, 50, n_samples)
    technical_difficulty = np.random.uniform(1.0, 5.0, n_samples)
    team_experience = np.random.uniform(1.0, 5.0, n_samples)
    expected_delivery_time = np.random.uniform(1, 24, n_samples)

    # 创建特征DataFrame
    X = pd.DataFrame({
        "function_points": function_points,
        "modules_count": modules_count,
        "interfaces_count": interfaces_count,
        "technical_difficulty": technical_difficulty,
        "team_experience": team_experience,
        "expected_delivery_time": expected_delivery_time
    })

    # 计算"真实"成本（加入一些随机噪声）
    base_cost = function_points * 1000
    module_factor = modules_count * 500
    interface_factor = interfaces_count * 300
    difficulty_factor = technical_difficulty * 1.5
    experience_factor = 1 / team_experience
    time_factor = 12 / expected_delivery_time

    # 计算成本并添加一些随机噪声
    cost = (base_cost + module_factor + interface_factor) * difficulty_factor * experience_factor * time_factor
    cost = cost * np.random.normal(1.0, 0.1, n_samples)  # 添加±10%的随机噪声

    # 创建目标Series
    y = pd.Series(cost, name="project_cost")

    return X, y


def main():
    """主函数：演示如何使用RegressionCostEstimator"""
    # 创建示例数据
    print("创建示例数据集...")
    X, y = create_sample_data(n_samples=200)

    # model_type: 回归模型类型，可选值: 'linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting'
    model_list = ['linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting']
    for model_type in model_list:
        # 创建并训练模型
        print("\n训练随机森林回归模型...")
        estimator = RegressionCostEstimator(model_type = model_type)
        estimator.train(X, y)


        # 交叉验证
        print("\n执行交叉验证...")
        estimator.cross_validate(X, y, cv=5)

        # 显示特征重要性
        print("\n特征重要性:")
        importance = estimator.feature_importance()
        for feature, value in importance.items():
            print(f"{feature}: {value:.4f}")



        # 预测新项目的成本
        print("\n预测新项目的成本:")
        new_project = {
            "function_points": 100,
            "modules_count": 10,
            "interfaces_count": 20,
            "technical_difficulty": 2,
            "team_experience": 3,
            "expected_delivery_time": 6
        }

        predicted_cost = estimator.predict(new_project)
        print(f"预测项目成本: {predicted_cost:.2f}元")

        # 保存模型
        model_path = "models/{}.pkl".format(model_type)
        print(f"\n保存模型到 {model_path}...")
        estimator.save_model(model_path)


if __name__ == "__main__":
    main()
