from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import PaymentTransaction
import uuid
from .phonepe_api import PhonePe
from django.conf import settings  # Import settings for secure management of constants
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from home.phonepe_constants import MERCHANT_ID, PHONE_PE_SALT, PHONE_PE_HOST, DJANGO_CUSTOM_REDIRECT_URL, DJANGO_CUSTOM_CALLBACK_URL

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in
            login(request, user)
            return redirect('/create_payment_transaction/')  # Redirect to the home page or desired page
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')  # Redirect back to login page if authentication fails

    return render(request, 'wallet/login.html')

# Your existing create_payment_transaction view code can go here...
def create_payment_transaction(request):
    context = {}  # Initialize context

    if request.method == 'POST':
        amount = request.POST.get('amount')
        first_name = request.POST.get('first_name')
        email_id = request.POST.get('email_id')
        mobile = request.POST.get('mobile')

        # Validate amount
        if not amount:
            return JsonResponse({"message": "Amount is required"}, status=400)
        
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return JsonResponse({"message": "Amount must be greater than zero"}, status=400)
            amount_cents = int(amount_float * 100)
        except ValueError:
            return JsonResponse({"message": "Invalid amount"}, status=400)

        # Use settings to fetch sensitive info
        phonepe = PhonePe(
            MERCHANT_ID,
            PHONE_PE_SALT,
            PHONE_PE_HOST,
            DJANGO_CUSTOM_REDIRECT_URL,
            DJANGO_CUSTOM_CALLBACK_URL
        )
        order_id = uuid.uuid4().hex
        try:
            order_data = phonepe.create_txn(order_id, amount_cents,email_id)
        except Exception as e:
            return JsonResponse({"message": "Error with payment API", "error": str(e)}, status=500)

        if order_data.get('code') == "PAYMENT_INITIATED":
            # Create payment transaction
            transaction, created = PaymentTransaction.objects.get_or_create(
                first_name=first_name,
                email_id=email_id,
                mobile=mobile,
                order_id=order_id,
                defaults={
                    'amount': amount_cents,
                    'status': "PENDING",
                    'message': order_data.get("message", ""),
                    'payment_link': order_data.get("data", {}).get("instrumentResponse", {}).get("redirectInfo", {}).get("url", ""),
                    'base_amount': amount_float,
                    'first_name': first_name,
                    'email_id': email_id,
                    'mobile': mobile    
                }
            )

            if created:
                return redirect(transaction.payment_link)
            else:
                return JsonResponse({"message": "Transaction already exists"}, status=400)
        else:
            return JsonResponse({"message": "Payment initiation failed", "error": order_data.get('message')}, status=500)

    return render(request, 'wallet/checkout.html', context)

def home(request):
    return render(request, 'wallet/index.html')


@csrf_exempt
def payment_status(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method. Only POST requests are allowed.")
    
    # Retrieve necessary data from POST request
    transaction_id = request.POST.get('transactionId')
    payment_status_code = request.POST.get('code')

    # Validate input data
    if not transaction_id or not payment_status_code:
        return HttpResponseBadRequest("Missing transactionId or payment status code.")

    try:
        # Fetch the latest transaction
        transaction = PaymentTransaction.objects.order_by('-create_at').first()
        if not transaction:
            return HttpResponseBadRequest("Transaction not found.")
        order_id = transaction.order_id

    except PaymentTransaction.DoesNotExist:
        return HttpResponseBadRequest("Transaction not found.")
    
    # Retrieve user's wallet and calculate coins
    #user_wallet = UserWallet.objects.get(user=transaction.user)
    #old_coins = user_wallet.total_balance
    
    coins_earned = transaction.base_amount * 10
    #description = f"Payment of {transaction.base_amount} was successful. You have earned {coins_earned} coins."

    # Update transaction based on payment status
    transaction.transactionId = transaction_id
    if payment_status_code == 'PAYMENT_SUCCESS':
        transaction.status = 'SUCCESS'

        # Record coin transaction
        #CoinTransaction.objects.create(
           # user=transaction.user,
            #transaction_type='Credit',
            #coins=coins_earned,
            #description=description,
            #)

        # Update user's wallet balance
        #user_wallet.total_balance = old_coins + coins_earned
        #user_wallet.save()

        message = f"Your transaction {transaction_id} was successful."
        alert_type = 'success'
    else:
        transaction.status = 'FAILED'
        message = f"Your transaction {transaction_id} failed."
        alert_type = 'danger'
    
    transaction.save()

    # Generate PDF invoice if payment was successful
    #file_name, pdf_generated = generate_invoice_pdf(order_id)

    # Prepare context for template rendering
    context = {
        'message': message,
        'alert_type': alert_type,
        #'file_name': file_name if pdf_generated else None,
        'success': payment_status_code == 'PAYMENT_SUCCESS',
      
    }
    if request.user.is_authenticated:
        #user_wallet = get_object_or_404(UserWallet, user=request.user)
        pass
        context.update({
         #"coins_total_balance": user_wallet.total_balance,
        })

    # Render the payment status template
    return render(request, 'wallet/payment_status.html', context)
