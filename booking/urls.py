from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('book-room/<int:room_id>/', views.book_room, name='book_room'),
    path('bookings/<int:booking_id>/', views.view_booking, name='view_booking'),
    path('test-form/', views.test_form_submission, name='test_form'),
    # Payment Gateway URLs
    path('payment/create-order/<int:room_id>/', views.create_payment_order, name='create_payment_order'),
    path('payment/process/<str:order_id>/', views.payment_process, name='payment_process'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('contact/', views.contact_view, name='contact_view'),
] 