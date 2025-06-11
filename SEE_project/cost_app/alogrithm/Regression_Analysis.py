from Regression_Analysis_model_train import RegressionCostEstimator


def Regression_Analysis(function_points,
                        modules_count,
                        interfaces_count,
                        technical_difficulty,
                        team_experience,
                        expected_delivery_time,
                        model_type: str
                        ):  # model_type: 回归模型类型，可选值: 'linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting'
    project = {
        "function_points": function_points,
        "modules_count": modules_count,
        "interfaces_count": interfaces_count,
        "technical_difficulty": technical_difficulty,
        "team_experience": team_experience,
        "expected_delivery_time": expected_delivery_time
    }
    model_path = "models/{}.pkl".format(model_type)
    estimator = RegressionCostEstimator(model_type)
    estimator.load_model(model_path)
    predicted_cost = estimator.predict(project)

    return round(predicted_cost, 2)


predicted_cost = Regression_Analysis(
    100, 10, 20, 2, 3, 6, 'linear'
)

print(predicted_cost)


def Regression_Analysis_all_models(function_points,
                                   modules_count,
                                   interfaces_count,
                                   technical_difficulty,
                                   team_experience,
                                   expected_delivery_time,
                                   ):
    model_list = ['linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting']
    predicted_cost_dict = {}

    project = {
        "function_points": function_points,
        "modules_count": modules_count,
        "interfaces_count": interfaces_count,
        "technical_difficulty": technical_difficulty,
        "team_experience": team_experience,
        "expected_delivery_time": expected_delivery_time
    }

    for model_type in model_list:
        model_path = "models/{}.pkl".format(model_type)
        estimator = RegressionCostEstimator(model_type)
        estimator.load_model(model_path)
        predicted_cost = estimator.predict(project)
        predicted_cost_dict[model_type] = round(predicted_cost, 2)

    return predicted_cost_dict


predicted_cost_dict = Regression_Analysis_all_models(
    100, 10, 20, 2, 3, 6
)

print(predicted_cost_dict)
