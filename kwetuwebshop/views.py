from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
import base64
import datetime
import requests


# Create your views here.
def index(request):
    # return HttpResponse('Hello World')
    products = Product.objects.all()
    return render(request, 'index.html',
                  {'products': products})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Get or initialize the cart in the session
    cart = request.session.get('cart', [])

    # Check if the product is already in the cart
    if product.id not in cart:
        # Add the product ID to the cart
        cart.append(product.id)
        request.session['cart'] = cart
        return redirect('view_cart')  # Redirect to the cart page
    else:
        # If the product is already in the cart, display a message or handle accordingly
        return render(request, 'product_already_in_cart.html', {'product': product})


def view_cart(request):
    # Retrieve products in the cart based on the stored IDs
    cart = request.session.get('cart', [])
    cart_products = Product.objects.filter(id__in=cart)

    return render(request, 'cart.html', {'cart_products': cart_products})


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Get or initialize the cart in the session
    cart = request.session.get('cart', [])

    # Check if the product is in the cart before attempting to remove
    if product.id in cart:
        cart.remove(product.id)
        request.session['cart'] = cart

    return redirect('view_cart')  # Redirect back to the cart page


def checkout(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phoneNumber')
        product = Product.objects.get()
        amount = product.price

        # Daraja M-Pesa integration
        consumer_key = 'ABVN0ZssyLAzGA48DG9HUpChsbjJ4WUu'
        consumer_secret = '6NBos0sbEaNLRIVy'
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_shortcode = '174379'

        base_url = 'https://sandbox.safaricom.co.ke'
        auth_url = base_url + '/oauth/v1/generate?grant_type=client_credentials'
        stk_push_url = base_url + '/mpesa/stkpush/v1/processrequest'
        auth_headers = {
            'Authorization': 'Basic ' + base64.b64encode((consumer_key + ':' + consumer_secret).encode('ascii')).decode(
                'ascii')}

        # Get access token
        auth_response = requests.get(auth_url, headers=auth_headers)
        access_token = auth_response.json().get('access_token')

        if access_token:
            # Prepare STK Push request
            stk_push_headers = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json'
            }
            stk_push_body = {
                'BusinessShortCode': business_shortcode,
                'Password': base64.b64encode(
                    (business_shortcode + passkey + datetime.datetime.now().strftime('%Y%m%d%H%M%S')).encode(
                        'ascii')).decode('ascii'),
                'Timestamp': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
                'TransactionType': 'CustomerPayBillOnline',
                'Amount': amount,
                'PartyA': phone_number,
                'PartyB': business_shortcode,
                'PhoneNumber': phone_number,
                'CallBackURL': 'https://5e44-105-160-82-216.ngrok-free.app',
                'AccountReference': 'Ecommerce',  # Update with your reference
                'TransactionDesc': 'payment'
            }

            # Initiate STK Push
            stk_push_response = requests.post(stk_push_url, headers=stk_push_headers, json=stk_push_body)

            if stk_push_response.status_code == 200:
                # STK Push initiated successfully
                messages.success(request, 'Payment initiated successfully. You will receive a prompt on your phone.')
                # Clear the cart after successful checkout
                request.session['cart'] = []
                return redirect('checkout')  # Redirect to a success page

    # If the request method is not POST or there was an error, redirect to the cart page
    return redirect('view_cart')