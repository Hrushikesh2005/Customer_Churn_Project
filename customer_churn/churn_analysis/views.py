from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from churn_analysis.services.handle_uploads import handle_uploaded_file
from churn_analysis.services.insights import results
from churn_analysis.models import ChurnAnalysis

import base64
from io import BytesIO
from matplotlib import pyplot as plt
from django.core.files.base import ContentFile


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
    # Fetch all analyses for the logged-in user
    analyses = ChurnAnalysis.objects.filter(user=request.user)
    context = {'analyses': analyses}
    return render(request, 'churn_analysis/home.html', context)


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
            has_churn_column = form.cleaned_data['has_churn_column']

            try:
                # Reset file pointer
                file.seek(0)
                
                total_results, modified_df = handle_uploaded_file(file, has_churn_column)
                
                # Save modified CSV to model
                csv_content = modified_df.to_csv(index=False)
                analysis = ChurnAnalysis.objects.create(
                    user=request.user,
                    filename=file.name,
                    churn_rate=total_results['churn_rate'],
                    accuracy=total_results['accuracy'],
                    has_churn_column=(has_churn_column == 'yes')
                )
                
                # Save the modified CSV file
                analysis.output_file.save(
                    f"analysis_{analysis.id}_{file.name}",
                    ContentFile(csv_content)
                )
                
                # Save input file too
                file.seek(0)
                analysis.input_file.save(f"input_{analysis.id}_{file.name}", file)
                
                # Call result view
                context = results(total_results['churn_rate'], total_results['churn_counts'], 
                                total_results['feature_importances'], total_results['accuracy'])
                
                # Store analysis ID in session for download
                request.session['current_analysis_id'] = analysis.id
                
                return render(request, "churn_analysis/results.html", context)
            
            except ValueError as e:
                form.add_error(None, str(e))
                return render(request, 'churn_analysis/upload.html', {'form': form})

    else:
        form = UploadFileForm()

    return render(request, 'churn_analysis/upload.html', {'form': form})

#-----------------DOWNLOAD_NEW_CSV VIEW-----------------

def download_csv(request):
    # Get analysis ID from POST or session
    analysis_id = request.POST.get('analysis_id') or request.session.get('current_analysis_id')
    
    if not analysis_id:
        return HttpResponse("No CSV file available for download.", status=404)
    
    try:
        analysis = ChurnAnalysis.objects.get(id=analysis_id, user=request.user)
        
        if not analysis.output_file:
            return HttpResponse("No CSV file found.", status=404)
        
        # Read the file from storage
        file_content = analysis.output_file.read()
        
        # Set up the HTTP response
        response = HttpResponse(file_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=analysis_{analysis_id}_output.csv'
        
        return response
    
    except ChurnAnalysis.DoesNotExist:
        return HttpResponse("Analysis not found.", status=404)





