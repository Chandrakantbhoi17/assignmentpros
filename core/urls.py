from django.urls import path
from .views import (
    HomeView,
    PrivacyPolicyView,
    ContactUsView,
    TermsAndConditionsView,
    ShippingPolicyView,
    CancellationRefundsView,
    RazorpayOrderCreateView,  # ✅ New CBV for Razorpay
    RazorpayPaymentVerificationView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('contact-us/', ContactUsView.as_view(), name='contact-us'),
    path('shipping-policy/', ShippingPolicyView.as_view(), name='shipping-policy'),
    path('terms-and-conditions/', TermsAndConditionsView.as_view(), name='terms-and-conditions'),
    path('cancellation-refunds/', CancellationRefundsView.as_view(), name='cancellation-refunds'),

    # ✅ Razorpay-related paths
    path('create-razorpay-order', RazorpayOrderCreateView.as_view(), name='razorpay_order_create'),
    path("verify-razorpay-payment/", RazorpayPaymentVerificationView.as_view(), name="payment_success"),

]
