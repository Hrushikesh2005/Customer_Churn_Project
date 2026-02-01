from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required  # Import this

from churn_analysis.services.handle_uploads import handle_uploaded_file
from churn_analysis.services.insights import result

from .forms import UploadFileForm

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
            return redirect('churn:login')  # ← Use URL name, not template path
    
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
            return redirect('churn:home')
        else:
            return render(request, 'churn_analysis/login.html', {
                'error_message': "Username or Password incorrect!"
            })
    
    return render(request, 'churn_analysis/login.html')

#-----------------(3)HOME VIEW-----------------

@login_required(login_url='churn:login')
def home(request):
    return render(request, 'churn_analysis/home.html')


#----------------- Logout view-----------------

def LogoutPage(request):
    logout(request)
    return redirect('churn:login')  # Use URL name instead of 'login'

#-----------------UPLOAD FILE VIEW-----------------
@login_required(login_url='churn:login')
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            has_churn_column = form.cleaned_data['has_churn_column']  # Get user's input about the churn column

            try:
                churn_rate, churn_counts, modified_df, feature_importances, accuracy = handle_uploaded_file(file, has_churn_column)

                # Save the modified DataFrame to a session for download
                request.session['modified_csv'] = modified_df.to_csv(index=False)
            
                # Call result view and pass feature importances and accuracy
                return result(request, churn_rate, churn_counts, feature_importances, accuracy)
            
            except ValueError as e:
                form.add_error(None, str(e))
                return render(request, 'churn_analysis/upload.html', {'form': form})

    else:
        form = UploadFileForm()

    return render(request, 'churn_analysis/upload.html', {'form': form})

#-----------------DOWNLOAD_NEW_CSV VIEW-----------------

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





