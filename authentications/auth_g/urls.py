# urls.py
from django.urls import path
from .views import user_registration,UserDataHTMLView,homepage,paymenthandler,verify_payment,send_registration_confirmation_email
app_name = 'auth_g'

urlpatterns = [
   
   path('registration/',user_registration,name='reg'),
   path('registration_dashboard/<int:id>/',UserDataHTMLView.as_view(),name='reg'),
   path('initiate_payment/', homepage, name='initiate-payment'),
   path('payment/callback/', paymenthandler, name='callback-payment'),
    path('payment/verify/<str:payment_id>/', verify_payment, name='verify-payment'),
    path('registrationemail/<int:user_id>/',send_registration_confirmation_email,name="email")
   
]
