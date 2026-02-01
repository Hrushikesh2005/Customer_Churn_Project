from sklearn.cluster import KMeans
import pandas as pd

def run_unsupervised_churn(df):
    kmeans = KMeans(n_clusters=2, random_state=42)
    clusters = kmeans.fit_predict(df)

    df['Churn'] = clusters
    churn_cluster = df['Churn'].value_counts().idxmin()
    df['Churn'] = (df['Churn'] == churn_cluster).astype(int)

    return df
