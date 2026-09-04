from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AvatarOptionsView,
    ForgotPasswordView,
    DefaultDeliveryAddressView,
    DeliveryAddressDetailView,
    DeliveryAddressListCreateView,
    LoginView,
    ProfileView,
    RegisterView,
    ResetPasswordView,
    SetDefaultDeliveryAddressView,
    ChangePasswordView,
    VerifyEmailView,
    ResendVerificationView,
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/avatar-options/', AvatarOptionsView.as_view(), name='avatar-options'),
    path('profile/addresses/', DeliveryAddressListCreateView.as_view(), name='delivery-address-list'),
    path('profile/addresses/default/', DefaultDeliveryAddressView.as_view(), name='delivery-address-default'),
    path('profile/addresses/<int:pk>/', DeliveryAddressDetailView.as_view(), name='delivery-address-detail'),
    path('profile/addresses/<int:pk>/set-default/', SetDefaultDeliveryAddressView.as_view(), name='delivery-address-set-default'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password')
]
