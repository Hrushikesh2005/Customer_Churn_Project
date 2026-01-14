from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required  # Import this
import pandas as pd
import matplotlib.pyplot as plt
from django.shortcuts import render
from .forms import UploadFileForm
# import plotly.express as px
from io import BytesIO
import base64
#********************************************************************
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from django.http import HttpResponse
from sklearn.decomposition import PCA
import csv
#latest

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

#********************************************************************

# Home page view with login_required decorator
@login_required(login_url='login')
def HomePage(request):
    return render(request, 'home.html')

#-----------------(1) Signup view-----------------

def SignUp(request):
    if request.method == 'POST':           # ← Button pressed (form submitted)
        # Process form data
        uname = request.POST.get('uname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        
        if password != cpassword:
            # Decision 1: Stay on signup page with error
            return HttpResponse("Password and Confirm Password doesn't match")
        else:
            # Decision 2: Create user and redirect to login
            my_user = User.objects.create_user(uname, email, password)
            my_user.save()
            return redirect('login')  # ← Django loads login page
    
    # If GET request (just viewing the page)
    return render(request, 'churn_analysis/signup.html')

#-----------------(2) Login view-----------------
def LoginPage(request):
    
    if request.method == 'POST':
    
        username = request.POST.get('username')
        password1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=password1)
    
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Username or Password incorrect!")
    
    return render(request, 'churn_analysis/login.html')

#-----------------(3)HOME VIEW-----------------

def home(request):
    return render(request, 'churn_analysis/home.html')


#----------------- Logout view-----------------

def LogoutPage(request):
    logout(request)
    return redirect('login')



#----------------- RESULT VIEW -----------------

def result(request, churn_rate, churn_counts, feature_importances, accuracy):
    # Plot churn distribution
    plt.figure(figsize=(8, 6))
    plt.pie(churn_counts.values, labels=['Not Churned', 'Churned'], autopct='%1.1f%%', startangle=90)
    plt.title('Customer Churn Distribution')

    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    chart_base64 = base64.b64encode(image_png).decode('utf-8')

    context = {
        'churn_rate': churn_rate,
        'chart': chart_base64,
        'feature_importances': feature_importances.to_dict(),
        'accuracy': accuracy
    }

    return render(request, 'churn_analysis/results.html', context)

#-----------------HANDLE UPLOADED FILE----------------- 

def handle_uploaded_file(file, has_churn_column):
    # Load the uploaded CSV file into a DataFrame
    df = pd.read_csv(file)

    df_preprocessed = preprocess_data(df)  # Preprocess the data

    # Supervised learning if churn column exists (based on user input)
    if has_churn_column == 'yes':
        # Check if the Churn column contains 'Yes'/'No' and map to 0/1
        if df['Churn'].dtype == 'object' and set(df['Churn'].unique()).issubset({'Yes', 'No'}):
            df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
        elif df['Churn'].dtype not in ['int64', 'bool', 'int32']:
            # Convert continuous Churn values to binary (e.g., threshold at median)
            threshold = df['Churn'].median()  # Define a threshold to categorize
            df['Churn'] = (df['Churn'] > threshold).astype(int)  # Convert to 0/1

        X = df_preprocessed.drop('Churn', axis=1)
        y = df_preprocessed['Churn']

        # Ensure that the churn column contains only two classes (0 or 1)
        if y.nunique() > 2:
            return HttpResponse("Error: Churn column should only have 0 or 1 values.", status=400)

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train a RandomForestClassifier for feature importance
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Feature importance
        feature_importances = pd.Series(model.feature_importances_, index=X_train.columns).sort_values(ascending=False)

        # Evaluate the model
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

    # Unsupervised learning (KMeans) if no churn column
    else:
        kmeans = KMeans(n_clusters=2, random_state=42)
        df['Churn'] = kmeans.fit_predict(df_preprocessed)

        churn_cluster = df['Churn'].value_counts().idxmin()
        df['Churn'] = (df['Churn'] == churn_cluster).astype(int)

        # Set dummy feature importance (for explanation)
        feature_importances = pd.Series([1] * df_preprocessed.shape[1], index=df_preprocessed.columns)

        accuracy = None  # Unsupervised, no accuracy

    churn_rate = round((df['Churn'].mean() * 100), 1)
    churn_counts = df['Churn'].value_counts()

    return churn_rate, churn_counts, df, feature_importances, accuracy

#-----------------PREPROCESSING THE DATA-----------------
#NEW CODE
def preprocess_data(df):
    # Handle missing values by forward filling
    df.fillna(method='ffill', inplace=True)

    # Encode categorical columns
    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    # Standardize numerical columns
    scaler = StandardScaler()
    df_scaled = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    return df_scaled

#-----------------UPLOAD FILE VIEW-----------------

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            has_churn_column = form.cleaned_data['has_churn_column']  # Get user's input about the churn column

            churn_rate, churn_counts, modified_df, feature_importances, accuracy = handle_uploaded_file(file, has_churn_column)

            # Save the modified DataFrame to a session for download
            request.session['modified_csv'] = modified_df.to_csv(index=False)
        
            # Call result view and pass feature importances and accuracy
            return result(request, churn_rate, churn_counts, feature_importances, accuracy)

    else:
        form = UploadFileForm()

    return render(request, 'churn_analysis/upload.html', {'form': form})


#-----------------DOWNLOAD_NEW_CSV FUNCTION-----------------

from django.http import HttpResponse

def download_csv(request):
    # Retrieve the CSV data from session storage
    modified_csv = request.session.get('modified_csv', '')

    if not modified_csv:
        return HttpResponse("No CSV file available for download.", status=404)

    # Set up the HTTP response with the CSV file
    response = HttpResponse(modified_csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=modified_data.csv'
    
    return response

#---------------------------------------------------





