# # churn_analysis/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),  # Ensure this matches the function name in views.py
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload_file'),
    path('SignUp/', views.SignUp, name='SignUp'),
    path('login/',views.LoginPage,name='login'),
]
