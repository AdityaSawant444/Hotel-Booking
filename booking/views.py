from django.contrib import messages
import booking
import stripe
from django.shortcuts import render
from django.conf import settings
from decimal import Decimal
from booking.form import BookingForm
from .models import Booking, Hotel, Room
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import razorpay
from django.urls import reverse

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.

def home(request):
    return render(request, 'home.html')

def contact(request):
  return render(request, 'contact.html')

def hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'hotel_list.html', {'hotels': hotels})

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = hotel.rooms.all()
    return render(request, 'hotel_detail.html', {'hotel': hotel, 'rooms': rooms})

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def booking_list(request):
    bookings = Booking.objects.all()
    return render(request, 'booking_list.html', {'bookings': bookings})

def create_razorpay_order(room, guest_data):
    """Create a Razorpay order"""
    try:
        order_id = f"ORDER_{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate total amount based on number of rooms
        num_rooms = int(guest_data.get('num_rooms', 1))
        total_amount = float(room.price) * num_rooms
        amount_paise = int(total_amount * 100)  # Convert to paise
        
        print(f"Payment calculation debug:")
        print(f"  Room price: {room.price}")
        print(f"  Number of rooms: {num_rooms}")
        print(f"  Total amount: {total_amount}")
        
        # Convert price to paise (Razorpay expects amount in paise)
        amount_in_paise = int(total_amount * 100)
        
        print(f"  Amount in paise: {amount_in_paise}")
        
        # Create Razorpay order
        order_data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': order_id,
            'notes': {
                'guest_name': guest_data['guest_name'],
                'guest_email': guest_data['guest_email'],
                'room_id': str(room.id),
                'num_rooms': str(num_rooms)
            }
        }
        
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        return {
            'order_id': order_id,
            'razorpay_order_id': razorpay_order['id'],
            'amount': amount_in_paise,
            'amount_rupees': total_amount,
            'currency': 'INR'
        }, order_id
        
    except Exception as e:
        raise Exception(f"Failed to create Razorpay order: {str(e)}")



def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    print(f"Book room view called for room_id: {room_id}")
    print(f"Request method: {request.method}")
    
    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        form = BookingForm(request.POST)
        print(f"Form is valid: {form.is_valid()}")
        if form.is_valid():
            print("Form is valid, processing...")
            try:
                # Get form data
                guest_data = {
                    'guest_name': form.cleaned_data['guest_name'],
                    'guest_email': form.cleaned_data['guest_email'],
                    'guest_phone': form.cleaned_data['guest_phone'],
                    'check_in': form.cleaned_data['check_in'],
                    'check_out': form.cleaned_data['check_out'],
                    'num_adults': form.cleaned_data['num_adults'],
                    'num_children': form.cleaned_data['num_children'],
                    'num_rooms': form.cleaned_data['num_rooms'],
                }
                print(f"Processing booking for room {room_id}")
                print(f"Guest data: {guest_data}")
                # Always create a new Razorpay order and update session with latest payment details
                order_response, order_id = create_razorpay_order(room, guest_data)
                print(f"Created order: {order_id}")
                print(f"Order response: {order_response}")
                calculated_total = float(room.price) * int(guest_data['num_rooms'])
                print(f"Calculated total amount (room.price * num_rooms): {room.price} * {guest_data['num_rooms']} = {calculated_total}")
                # Store booking details in session for later use
                request.session['pending_booking'] = {
                    'room_id': room_id,
                    'guest_name': guest_data['guest_name'],
                    'guest_email': guest_data['guest_email'],
                    'guest_phone': guest_data['guest_phone'],
                    'check_in': guest_data['check_in'].strftime('%Y-%m-%d'),
                    'check_out': guest_data['check_out'].strftime('%Y-%m-%d'),
                    'num_adults': guest_data['num_adults'],
                    'num_children': guest_data['num_children'],
                    'num_rooms': guest_data['num_rooms'],
                    'order_id': order_id,
                    'total_amount': calculated_total
                }
                print(f"Session pending_booking: {request.session['pending_booking']}")
                # Always update payment_details in session with the latest order_response
                request.session['payment_details'] = order_response
                print(f"Session payment_details: {request.session['payment_details']}")
                request.session.modified = True
                print(f"Redirecting to payment process with order_id: {order_id}")
                return redirect('payment_process', order_id=order_id)
            except Exception as e:
                # If payment creation fails, show error
                print(f"Payment initialization failed: {str(e)}")
                form.add_error(None, f"Payment initialization failed: {str(e)}")
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = BookingForm()
    return render(request, 'book_room.html', {'form': form, 'room': room})

def view_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'view_booking.html', {'booking': booking})

def create_payment_order(request, room_id):
    """Create a Razorpay payment order for room booking"""
    if request.method == 'POST':
        try:
            room = get_object_or_404(Room, id=room_id)
            data = json.loads(request.body)
            
            # Get booking details from request
            guest_data = {
                'guest_name': data.get('guest_name', ''),
                'guest_email': data.get('guest_email', ''),
                'guest_phone': data.get('guest_phone', ''),
                'check_in': data.get('check_in', ''),
                'check_out': data.get('check_out', ''),
                'num_adults': data.get('num_adults', 1),
                'num_children': data.get('num_children', 0),
                'num_rooms': data.get('num_rooms', 1),
            }
            
            # Create Razorpay order
            order_response, order_id = create_razorpay_order(room, guest_data)
            
            # Store booking details in session for later use
            request.session['pending_booking'] = {
                'room_id': room_id,
                'guest_name': guest_data['guest_name'],
                'guest_email': guest_data['guest_email'],
                'guest_phone': guest_data['guest_phone'],
                'check_in': guest_data['check_in'],
                'check_out': guest_data['check_out'],
                'num_adults': guest_data['num_adults'],
                'num_children': guest_data['num_children'],
                'num_rooms': guest_data['num_rooms'],
                'order_id': order_id,
                'total_amount': float(room.price) * int(guest_data['num_rooms'])
            }
            
            return JsonResponse({
                'success': True,
                'order_id': order_id,
                'razorpay_order_id': order_response['razorpay_order_id'],
                'amount': order_response['amount'],
                'currency': order_response['currency']
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@csrf_exempt
def payment_webhook(request):
    """Handle Razorpay payment webhooks"""
    if request.method == 'POST':
        try:
            # Get webhook data
            webhook_data = json.loads(request.body)
            
            # Verify webhook signature (you should implement proper signature verification)
            # For now, we'll process without verification in test mode
            
            payment_id = webhook_data.get('payload', {}).get('payment', {}).get('entity', {}).get('id')
            order_id = webhook_data.get('payload', {}).get('payment', {}).get('entity', {}).get('order_id')
            payment_status = webhook_data.get('payload', {}).get('payment', {}).get('entity', {}).get('status')
            
            if payment_status == 'captured':
                # Get pending booking from session
                pending_booking = request.session.get('pending_booking')
                if pending_booking:
                    # Create the actual booking
                    room = get_object_or_404(Room, id=pending_booking['room_id'])
                    
                    booking = Booking.objects.create(
                        room=room,
                        guest_name=pending_booking['guest_name'],
                        guest_email=pending_booking['guest_email'],
                        guest_phone=pending_booking['guest_phone'],
                        check_in=pending_booking['check_in'],
                        check_out=pending_booking['check_out'],
                        num_adults=pending_booking['num_adults'],
                        num_children=pending_booking['num_children'],
                        total_amount=pending_booking['total_amount'],
                        payment_status='PAID',
                        order_id=pending_booking['order_id']
                    )
                    
                    # Clear session data
                    del request.session['pending_booking']
                    
                    return JsonResponse({'success': True})
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def payment_process(request, order_id):
    """Process payment with Razorpay"""
    payment_details = request.session.get('payment_details')

    # Debug logging
    print(f"Payment Process - Order ID: {order_id}")
    print(f"Payment Details in Session: {payment_details}")
    if payment_details:
        print(f"Amount in payment_details: {payment_details.get('amount')}")
        print(f"Amount_rupees in payment_details: {payment_details.get('amount_rupees')}")
    else:
        print("No payment details found in session")

    if not payment_details:
        return redirect('home')

    if payment_details.get('order_id') != order_id:
        print(f"Order ID mismatch. Expected: {order_id}, Got: {payment_details.get('order_id')}")
        return redirect('home')

    return render(request, 'payment_process.html', {
        'payment_details': payment_details,
        'order_id': order_id,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    })

def test_form_submission(request):
    """Test view to debug form submission"""
    if request.method == 'POST':
        print("Test form submitted!")
        print(f"POST data: {request.POST}")
        return JsonResponse({'status': 'success', 'data': dict(request.POST)})
    return render(request, 'test_form.html')

def payment_success(request):
    """Handle successful payment redirect and save booking if not already saved."""
    # Try to create booking from session if it exists
    pending_booking = request.session.get('pending_booking')
    if pending_booking:
        try:
            room = get_object_or_404(Room, id=pending_booking['room_id'])
            # Check if booking with this order_id already exists
            if not Booking.objects.filter(order_id=pending_booking['order_id']).exists():
                Booking.objects.create(
                    room=room,
                    guest_name=pending_booking['guest_name'],
                    guest_email=pending_booking['guest_email'],
                    guest_phone=pending_booking['guest_phone'],
                    check_in=pending_booking['check_in'],
                    check_out=pending_booking['check_out'],
                    num_adults=pending_booking['num_adults'],
                    num_children=pending_booking['num_children'],
                    total_amount=pending_booking['total_amount'],
                    payment_status='PAID',
                    order_id=pending_booking['order_id']
                )
            # Remove pending_booking from session
            del request.session['pending_booking']
            request.session.modified = True
        except Exception as e:
            print(f"Error saving booking in payment_success: {e}")
    return render(request, 'payment_success.html')

def payment_failure(request):
    """Handle failed payment redirect"""
    return render(request, 'payment_failure.html')


def contact_view(request):
    """Contact view to handle contact form submissions"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Here you would typically save the contact message to the database or send an email
        print(f"Contact form submitted by {name} ({email}): {message}")
        
        messages.success(request,  "Thank you for contacting us! We will get back to you soon")
        return redirect('home')
        
    
    return render(request, 'contact.html')




