from django.urls import path
from app import views


urlpatterns = [

    # Login / Logout
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Guests
    path('guests/', views.guest_list, name='guest_list'),
    path('guests/add/', views.guest_create, name='guest_create'),
    path('guests/<int:guest_id>/', views.guest_detail, name='guest_detail'),
    path('guests/<int:guest_id>/edit/', views.guest_update, name='guest_update'),

    # Room Types
    path('room-types/', views.room_type_list, name='room_type_list'),
    path('room-types/add/', views.room_type_create, name='room_type_create'),

    # Rooms
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/add/', views.room_create, name='room_create'),
    path(
        'rooms/<int:room_id>/status/',
        views.room_update_status,
        name='room_update_status'
    ),

    # Bookings
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/add/', views.booking_create, name='booking_create'),
    path(
        'bookings/<int:booking_id>/',
        views.booking_detail,
        name='booking_detail'
    ),
    path(
        'bookings/<int:booking_id>/cancel/',
        views.booking_cancel,
        name='booking_cancel'
    ),

    # Check-in
    path(
        'checkin/<int:booking_id>/',
        views.checkin_create,
        name='checkin_create'
    ),

    # Check-out
    path(
        'checkout/<int:checkin_id>/',
        views.checkout_create,
        name='checkout_create'
    ),

    # Services
    path('services/', views.service_list, name='service_list'),
    path('services/add/', views.service_create, name='service_create'),

    # Bills
    path('bills/', views.bill_list, name='bill_list'),
    path(
        'bills/add/<int:booking_id>/',
        views.bill_create,
        name='bill_create'
    ),

    # Payments
    path(
        'payments/add/<int:bill_id>/',
        views.payment_create,
        name='payment_create'
    ),
]