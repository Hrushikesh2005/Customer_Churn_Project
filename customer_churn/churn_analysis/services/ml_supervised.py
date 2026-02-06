from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

def run_supervised_churn(df):
    X = df.drop('Churn', axis=1)
    y = df['Churn']

    if y.nunique() > 2:
        raise ValueError("Churn column should only have 0 or 1 values (2 classes). Found {} classes.".format(y.nunique()))

    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    feature_importance = pd.Series(
        model.feature_importances_, index=X.columns
    ).sort_values(ascending=False)

    return {
        # "model": model,
        "accuracy": accuracy,
        "feature_importance": feature_importance
    }
