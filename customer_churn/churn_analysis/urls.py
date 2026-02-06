# # churn_analysis/urls.py
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),  # Ensure this matches the function name in views.py
# ]

# path('', views.upload_file, name='upload_file')
# #    │       │                    │
# #    │       │                    └── URL Name (for reversing)
# #    │       └── View Function (what gets called)
# #    └── URL Pattern (what user types)

from django.urls import path
from . import views

app_name = 'churn'  # ← Add this line
# This creates the mapping: namespace:url_name → app_name:url_name

urlpatterns = [
    path('', views.SignUp, name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('home/', views.home, name='home'),
    path('uploads/', views.upload_file, name='upload_file'),
    path('download_csv/', views.download_csv, name='download_csv'),
    path('logout/', views.LogoutPage, name='logout'),
]
