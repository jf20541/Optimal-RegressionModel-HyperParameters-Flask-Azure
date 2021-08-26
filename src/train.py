import pandas as pd
from math import sqrt
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import optuna
import config


df = pd.read_csv(config.CLEAN_FILE)
targets = df.price.values.reshape(-1, 1)
features = df.drop("price", axis=1).values
x_train, x_test, y_train, y_test = train_test_split(features, targets, test_size=0.25)


def create_model(trial):
    model_type = trial.suggest_categorical(
        "model_type",
        [
            "DecisionTreeRegressor",
            "RandomForestRegressor",
            "XGBRegressor",
        ],
    )

    if model_type == "DecisionTreeRegressor":
        max_depth = trial.suggest_int("max_depth", 5, 10)
        min_samples_split = trial.suggest_int("min_samples_split", 2, 20)
        min_samples_leaf = trial.suggest_int("min_samples_leaf", 2, 20)

        model = DecisionTreeRegressor(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
        )

    if model_type == "RandomForestRegressor":
        n_estimators = trial.suggest_int("n_estimators", 100, 1000)
        max_depth = trial.suggest_int("max_depth", 5, 20)
        min_samples_split = trial.suggest_int("min_samples_split", 2, 20)
        min_samples_leaf = trial.suggest_int("min_samples_leaf", 2, 20)
        max_features = trial.suggest_categorical(
            "max_features", ["auto", "sqrt", "log2"]
        )

        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
        )

    if model_type == "XGBRegressor":
        eta = trial.suggest_discrete_uniform("eta", 0.1, 1.0, 0.1)
        gamma = trial.suggest_discrete_uniform("gamma", 0.1, 1.0, 0.1)
        max_depth = trial.suggest_int("max_depth", 5, 10)
        min_child_weight = trial.suggest_int("min_child_weight", 1, 5)
        subsample = trial.suggest_discrete_uniform("subsample", 0.1, 1.0, 0.1)

        model = XGBRegressor(
            eta=eta,
            gamma=gamma,
            max_depth=max_depth,
            min_child_weight=min_child_weight,
            subsample=subsample,
        )

    if trial.should_prune():
        raise optuna.TrialPruned()

    return model


def model_performance(model, x_test, y_test):
    pred = model.predict(x_test)
    return sqrt(mean_squared_error(y_test, pred))


def objective(trial):
    model = create_model(trial)
    model.fit(x_train, y_train.ravel())
    return model_performance(model, x_test, y_test)


if __name__ == "__main__":
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=50)

    # get optimal model and its hyper-parameters
    best_model = create_model(study.best_trial)
    best_model.fit(x_train, y_train.ravel())
    trial = study.best_trial
    print(f"Performance: {model_performance(best_model, x_test, y_test)}")
    print("Best hyperparameters: {}".format(trial.params))

# 124225.85791740331
# Best hyperparameters: {'model_type': 'RandomForestRegressor', 'n_estimators': 849, 'max_depth': 15, 'min_samples_split': 4, 'min_samples_leaf': 2, 'max_features': 'log2'}


# Performance: 117951.41601946934
# Best hyperparameters: {'model_type': 'RandomForestRegressor', 'n_estimators': 951, 'max_depth': 16, 'min_samples_split': 5, 'min_samples_leaf': 4, 'max_features': 'auto'}
