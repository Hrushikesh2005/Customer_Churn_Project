from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

from churn_analysis.services.preprocessing import preprocess_data
from churn_analysis.services.ml_supervised import run_supervised_churn
from churn_analysis.services.ml_unsupervised import run_unsupervised_churn

#-----------------HANDLE UPLOADED FILE----------------- 

def handle_uploaded_file(file, has_churn_column):
    # Load the uploaded CSV file into a DataFrame
    df = pd.read_csv(file)

    df_preprocessed = preprocess_data(df)  # Preprocess the data

    # Supervised learning if churn column exists (based on user input)
    if has_churn_column == 'yes':
        
        results = run_supervised_churn(df_preprocessed)
        
        feature_importances = results['feature_importance']
        accuracy = results['accuracy']  
        model = results['model']

    # Unsupervised learning (KMeans) if no churn column
    else:
        df = run_unsupervised_churn(df_preprocessed)
        # Set dummy feature importance (for explanation)
        feature_importances = pd.Series([1] * df_preprocessed.shape[1], index=df_preprocessed.columns)
        accuracy = None  # Unsupervised, no accuracy

    churn_rate = round((df['Churn'].mean() * 100), 1)
    churn_counts = df['Churn'].value_counts()

    return churn_rate, churn_counts, df, feature_importances, accuracy
