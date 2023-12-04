from django.urls import path
from .views import *
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name="index"),
    path('signup/', signup, name="signup"),
    path('user_login/', user_login, name="user_login"),
    path('index2/', index2, name="index2"),
    path('index3/', index3, name="index3"),  # Add URL pattern for index3
    path('logout/', logout, name="logout"),
    path('adminreg/', adminreg, name="adminreg"),
    path('booking/<int:car_id>/', booking, name='booking'),
    path('check_user_exists/', check_user_exists, name='check_user_exists'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('userprofile/', user_profile, name="user_profile"),
    path('update_user_details/', update_user_details, name="update_user_details"),
    path('owners/', owners, name="owners"),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('download-pdf/<str:car_owner_email>/', views.download_pdf, name='download_pdf'),
    path('addcar/', addcar, name="addcar"), 
    path('car_details/<int:car_id>/', car_details, name='car_details'),
    path('booking/<int:car_id>/<str:car_owner_id>/<str:user_id>/', booking, name='booking'),
    path('car_details/<int:car_id>/<str:user_id>/', views.car_details, name='car_details'),# Add URL pattern for index3
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)