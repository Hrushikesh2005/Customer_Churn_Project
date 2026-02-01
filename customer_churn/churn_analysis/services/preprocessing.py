from sklearn.preprocessing import StandardScaler, LabelEncoder
import pandas as pd

def preprocess_data(df):
    df = df.copy()
    df.fillna(method='ffill', inplace=True)

    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    scaler = StandardScaler()
    df_scaled = pd.DataFrame(
        scaler.fit_transform(df),
        columns=df.columns
    )
    return df_scaled
