from sklearn.preprocessing import StandardScaler, LabelEncoder
import pandas as pd

def preprocess_data(df):
    df = df.copy()
    df = df.ffill()

    # Separate churn column if it exists (to preserve it as discrete 0/1)
    has_churn = 'Churn' in df.columns
    if has_churn:
        churn_column = df['Churn'].copy()
        df = df.drop('Churn', axis=1)

    # Encode categorical columns
    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    # Scale only the feature columns (not the target)
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(
        scaler.fit_transform(df),
        columns=df.columns
    )
    
    # Add back the churn column (encoded but not scaled)
    if has_churn:
        # Encode churn column if it's not already numeric
        if churn_column.dtype == 'object':
            le = LabelEncoder()
            df_scaled['Churn'] = le.fit_transform(churn_column)
        else:
            df_scaled['Churn'] = churn_column.values
    
    return df_scaled
