# auth_g/views.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from allauth.socialaccount.models import SocialAccount
from .models import User,team_members,PaymentTransaction
from django.shortcuts import render,redirect
from .forms import UserRegistrationForm
from .serializers import UserSerializer, TeamMembersSerializer
from rest_framework.views import APIView
from django.views import View
import uuid
from django.http import JsonResponse
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

from django.core.mail import send_mail

def my_view(request):
    return render(request, 'index.html')

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def user_registration(request):
    users = request.user

    try:
        google_social_account = users.socialaccount_set.get(provider='Google')
    except SocialAccount.DoesNotExist:
        return Response({'error': 'User not authenticated with Google OAuth'}, status=status.HTTP_400_BAD_REQUEST)

    google_profile_data = google_social_account.extra_data

    # Pre-fill some fields from Google OAuth data
    leader_name = google_profile_data.get('name')
    leader_email = google_profile_data.get('email')
    profile_photo_url = google_profile_data.get('picture')



    print(leader_name)
    print(leader_email)
    print(profile_photo_url)
    """ return Response(google_profile_data)
 """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Check if the email already exists
            if User.objects.filter(leader_email=leader_email).exists():
                return Response({'error': 'Email already exists. Please use a different email.'}, status=status.HTTP_400_BAD_REQUEST)
            

            team_member = team_members(
                teammember1_name=form.cleaned_data['teammember1_name'],
                teammember1_email=form.cleaned_data['teammember1_email'],
                role1=form.cleaned_data['role1'],
                teammember2_name=form.cleaned_data['teammember2_name'],
                teammember2_email=form.cleaned_data['teammember2_email'],
                role2=form.cleaned_data['role2'],
                teammember3_name=form.cleaned_data['teammember3_name'],
                teammember3_email=form.cleaned_data['teammember3_email'],
                role3=form.cleaned_data['role3']
            )

            # Save the team_member instance to the database
            team_member.save()

            # Save the form data to the database
            #user = form.save(commit=False)  # Commit=False to set additional fields
            user=User()
            user.leader_name = leader_name
            user.leader_email = leader_email
            user.profile_photo_url = profile_photo_url
            user.save()


            
            return Response({'message': 'User registration successful'}, status=status.HTTP_201_CREATED)
    else:
        form = UserRegistrationForm()

    context = {
        'google_profile_data': google_profile_data,
        'form': form,
    }
    return render(request, 'registration_form.html', context)



class UserDataHTMLView(View):
    def get(self, request, id):
        try:
            # Retriving user data and team members data based on the provided ID
            user = User.objects.get(id=id)
            user_serializer = UserSerializer(user)

            team_members_data = team_members.objects.filter(leader=id)
            team_members_serializer = TeamMembersSerializer(team_members_data, many=True)

            context = {
                'user': user_serializer.data,
                'team_members': team_members_serializer.data,
            }
            if user.payment_amount != 0.00:
                context['registration_successful'] = True
            else:
                context['registration_successful'] = False

            return render(request, 'user_data.html', context)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        

razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def generate_unique_receipt():
    return str(uuid.uuid4())

def homepage(request):
    user = request.GET.get('user_id')
    print(user)

    currency = 'INR'
    amount = 20*100

    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        payment_capture='0'
    ))

    razorpay_order_id = razorpay_order['id']
    callback_url = 'payment/callback/'

    context = {
        'user':user,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
        'callback_url': callback_url
    }

    return render(request, 'indexs.html', context=context)

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            use=request.POST.get('user','')
            mod=User.objects.get(pk=use)

            if mod.payment_amount != 0:
                return HttpResponseBadRequest('Payment already done')
            

            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            result = razorpay_client.utility.verify_payment_signature(params_dict)

            if result is not None:
                amount = 2000

                try:
                    razorpay_client.payment.capture(payment_id, amount)
                    mod.payment_amount=20
                    mod.save()
                    transaction = PaymentTransaction(
                        user=use,
                        amount=amount,
                        currency='INR',
                        receipt=razorpay_order_id,
                        razorpay_order_id=razorpay_order_id,
                        razorpay_payment_id=payment_id,
                        razorpay_signature=signature,
                        payment_status='Process'
                    )
                    transaction.save()
                    return render(request, 'paymentsuccess.html')
                except:
                    return render(request, 'paymentfail.html')
            else:
                return render(request, 'paymentfail.html')
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()
    

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay

@csrf_exempt
def verify_payment(request, payment_id):
    razorpay_key_id = 'rzp_test_kWULZhVJWOB8xL'
    razorpay_key_secret = 'dJHQwpE5zpUxRFDSQXeCP5p'
    razorpay_client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

    if PaymentTransaction.objects.filter(razorpay_payment_id=payment_id).exists():
        payment = PaymentTransaction.objects.get(razorpay_payment_id=payment_id)
        payment.payment_status='success'
        payment.save()
        return JsonResponse({'status': 'Payment Verified and Updated'}, status=200)
    else:
        return JsonResponse({'error': 'Payment not found'}, status=404)



@csrf_exempt
def send_registration_confirmation_email(request, user_id):
    if request.method == "GET":
        try:
            user = User.objects.get(id=user_id)
            print(user.leader_name)
            team_info = team_members.objects.get(leader=user_id)
            subject = "Congratulations, Registration Successful"
            message = f"Hello {user.leader_name},\n\n"
            message += f"Team Member 1: {team_info.teammember1_name}, Email: {team_info.teammember1_email}\n"
            message += f"Team Member 2: {team_info.teammember2_name}, Email: {team_info.teammember2_email}\n"
            message += f"Team Member 3: {team_info.teammember3_name}, Email: {team_info.teammember3_email}"

            from_email = "your_email@gmail.com" 

            try:
                send_mail(subject, message, from_email, [user.leader_email])
                return JsonResponse({"message": "Email sent successfully"}, status=200)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        except team_members.DoesNotExist:
            return JsonResponse({"error": "Team members not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)