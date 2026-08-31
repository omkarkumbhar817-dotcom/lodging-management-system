from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import (
    User,
    Guest,
    RoomType,
    Room,
    Booking,
    CheckIn,
    CheckOut,
    Service,
    Bill,
    Payment,
)


# =========================
# LOGIN
# =========================

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')

        return render(
            request,
            'login.html',
            {'error': 'Invalid username or password'}
        )

    return render(request, 'login.html')
def user_logout(request):
    logout(request)
    return redirect('login')


# =========================
# DASHBOARD
# =========================

@login_required
def dashboard(request):
    context = {
        'total_guests': Guest.objects.count(),
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.filter(status='available').count(),
        'booked_rooms': Room.objects.filter(status='booked').count(),
        'occupied_rooms': Room.objects.filter(status='occupied').count(),
        'total_bookings': Booking.objects.count(),
        'active_bookings': Booking.objects.filter(
            status='confirmed'
        ).count(),
        'total_bills': Bill.objects.count(),
        'pending_bills': Bill.objects.filter(
            payment_status='pending'
        ).count(),
    }

    return render(request, 'dashboard.html', context)


# =========================
# GUESTS
# =========================
@login_required
def guest_list(request):
    guests = Guest.objects.all().order_by('-created_at')

    search = request.GET.get('search')

    if search:
        guests = guests.filter(
            Q(full_name__icontains=search) |
            Q(contact_number__icontains=search) |
            Q(identity_number__icontains=search)
        )

    return render(
        request,
        'guests/guest_list.html',
        {'guests': guests}
    )


@login_required
def guest_create(request):
    if request.method == 'POST':
        Guest.objects.create(
            full_name=request.POST.get('full_name'),
            address=request.POST.get('address'),
            contact_number=request.POST.get('contact_number'),
            email=request.POST.get('email') or None,
            identity_type=request.POST.get('identity_type'),
            identity_number=request.POST.get('identity_number'),
        )

        messages.success(request, 'Guest registered successfully.')
        return redirect('guest_list')

    return render(request, 'guests/guest_form.html')


@login_required
def guest_detail(request, guest_id):
    guest = get_object_or_404(Guest, guest_id=guest_id)

    bookings = Booking.objects.filter(
        guest=guest
    ).order_by('-booking_date')

    return render(
        request,
        'guests/guest_detail.html',
        {
            'guest': guest,
            'bookings': bookings,
        }
    )


@login_required
def guest_update(request, guest_id):
    guest = get_object_or_404(Guest, guest_id=guest_id)

    if request.method == 'POST':
        guest.full_name = request.POST.get('full_name')
        guest.address = request.POST.get('address')
        guest.contact_number = request.POST.get('contact_number')
        guest.email = request.POST.get('email') or None
        guest.identity_type = request.POST.get('identity_type')
        guest.identity_number = request.POST.get('identity_number')

        guest.save()

        messages.success(request, 'Guest details updated successfully.')
        return redirect('guest_list')

    return render(
        request,
        'guests/guest_form.html',
        {'guest': guest}
    )


# =========================
# ROOMS
# =========================

@login_required
def room_list(request):
    rooms = Room.objects.select_related(
        'room_type'
    ).order_by('room_number')

    return render(
        request,
        'rooms/room_list.html',
        {'rooms': rooms}
    )


@login_required
def room_create(request):
    room_types = RoomType.objects.all()

    if request.method == 'POST':
        room_type_id = request.POST.get('room_type')

        Room.objects.create(
            room_number=request.POST.get('room_number'),
            room_type_id=room_type_id,
            floor_number=request.POST.get('floor_number'),
            status=request.POST.get('status', 'available'),
        )

        messages.success(request, 'Room added successfully.')
        return redirect('room_list')

    return render(
        request,
        'rooms/room_form.html',
        {'room_types': room_types}
    )


@login_required
def room_update_status(request, room_id):
    room = get_object_or_404(Room, room_id=room_id)

    if request.method == 'POST':
        room.status = request.POST.get('status')
        room.save()

        messages.success(request, 'Room status updated.')
        return redirect('room_list')

    return render(
        request,
        'rooms/room_status.html',
        {'room': room}
    )


# =========================
# ROOM TYPES
# =========================

@login_required
def room_type_list(request):
    room_types = RoomType.objects.all().order_by('name')

    return render(
        request,
        'rooms/room_type_list.html',
        {'room_types': room_types}
    )


@login_required
def room_type_create(request):
    if request.method == 'POST':
        RoomType.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            tariff=request.POST.get('tariff'),
        )

        messages.success(request, 'Room type added successfully.')
        return redirect('room_type_list')

    return render(request, 'rooms/room_type_form.html')


# =========================
# BOOKINGS
# =========================

@login_required
def booking_list(request):
    bookings = Booking.objects.select_related(
        'guest',
        'room',
        'room__room_type'
    ).order_by('-booking_date')

    return render(
        request,
        'bookings/booking_list.html',
        {'bookings': bookings}
    )


@login_required
def booking_create(request):
    guests = Guest.objects.all()
    rooms = Room.objects.filter(status='available')

    if request.method == 'POST':
        guest_id = request.POST.get('guest')
        room_id = request.POST.get('room')
        check_in_date = request.POST.get('check_in_date')
        check_out_date = request.POST.get('check_out_date')

        room = get_object_or_404(
            Room,
            room_id=room_id
        )

        # Check whether the room is already booked
        overlapping_booking = Booking.objects.filter(
            room=room,
            status='confirmed',
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
        ).exists()

        if overlapping_booking:
            messages.error(
                request,
                'This room is already booked for the selected dates.'
            )

            return redirect('booking_create')

        booking = Booking.objects.create(
            guest_id=guest_id,
            room_id=room_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status='confirmed',
        )

        room.status = 'booked'
        room.save()

        messages.success(
            request,
            f'Booking #{booking.booking_id} created successfully.'
        )

        return redirect('booking_list')

    return render(
        request,
        'bookings/booking_form.html',
        {
            'guests': guests,
            'rooms': rooms,
        }
    )


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related(
            'guest',
            'room',
            'room__room_type'
        ),
        booking_id=booking_id
    )

    return render(
        request,
        'bookings/booking_detail.html',
        {'booking': booking}
    )


@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(
        Booking,
        booking_id=booking_id
    )

    if booking.status == 'confirmed':
        booking.status = 'cancelled'
        booking.save()

        room = booking.room
        room.status = 'available'
        room.save()

        messages.success(
            request,
            'Booking cancelled successfully.'
        )

    return redirect('booking_list')


# =========================
# CHECK-IN
# =========================

@login_required
def checkin_create(request, booking_id):
    booking = get_object_or_404(
        Booking,
        booking_id=booking_id
    )

    if booking.status != 'confirmed':
        messages.error(
            request,
            'Only confirmed bookings can be checked in.'
        )
        return redirect('booking_list')

    if CheckIn.objects.filter(booking=booking).exists():
        messages.error(
            request,
            'This booking has already been checked in.'
        )
        return redirect('booking_list')

    if request.method == 'POST':
        CheckIn.objects.create(
            booking=booking,
            guest=booking.guest,
            room=booking.room,
        )

        booking.room.status = 'occupied'
        booking.room.save()

        messages.success(
            request,
            'Guest checked in successfully.'
        )

        return redirect('booking_list')

    return render(
        request,
        'checkin/checkin_form.html',
        {'booking': booking}
    )


# =========================
# CHECK-OUT
# =========================

@login_required
def checkout_create(request, checkin_id):
    checkin = get_object_or_404(
        CheckIn,
        checkin_id=checkin_id
    )

    if CheckOut.objects.filter(checkin=checkin).exists():
        messages.error(
            request,
            'This guest has already checked out.'
        )
        return redirect('booking_list')

    if request.method == 'POST':
        checkout_date = timezone.now().date()

        number_of_nights = (
            checkout_date - checkin.booking.check_in_date
        ).days

        if number_of_nights < 1:
            number_of_nights = 1

        CheckOut.objects.create(
            checkin=checkin,
            number_of_nights=number_of_nights,
        )

        booking = checkin.booking
        booking.status = 'completed'
        booking.save()

        room = checkin.room
        room.status = 'housekeeping'
        room.save()

        messages.success(
            request,
            'Guest checked out successfully.'
        )

        return redirect('booking_list')

    return render(
        request,
        'checkout/checkout_form.html',
        {'checkin': checkin}
    )


# =========================
# SERVICES
# =========================

@login_required
def service_list(request):
    services = Service.objects.all().order_by('service_name')

    return render(
        request,
        'services/service_list.html',
        {'services': services}
    )


@login_required
def service_create(request):
    if request.method == 'POST':
        Service.objects.create(
            service_name=request.POST.get('service_name'),
            price=request.POST.get('price'),
        )

        messages.success(
            request,
            'Service added successfully.'
        )

        return redirect('service_list')

    return render(
        request,
        'services/service_form.html'
    )


# =========================
# BILLS
# =========================

@login_required
def bill_list(request):
    bills = Bill.objects.select_related(
        'booking',
        'booking__guest'
    ).order_by('-bill_date')

    return render(
        request,
        'billing/bill_list.html',
        {'bills': bills}
    )


@login_required
def bill_create(request, booking_id):
    booking = get_object_or_404(
        Booking,
        booking_id=booking_id
    )

    if hasattr(booking, 'bill'):
        messages.error(
            request,
            'A bill already exists for this booking.'
        )
        return redirect('bill_list')

    if request.method == 'POST':
        number_of_nights = int(
            request.POST.get('number_of_nights', 1)
        )

        room_amount = (
            booking.room.room_type.tariff *
            number_of_nights
        )

        service_amount = request.POST.get(
            'service_amount',
            0
        )

        total_amount = (
            room_amount +
            float(service_amount)
        )

        Bill.objects.create(
            booking=booking,
            number_of_nights=number_of_nights,
            room_amount=room_amount,
            service_amount=service_amount,
            total_amount=total_amount,
        )

        messages.success(
            request,
            'Bill created successfully.'
        )

        return redirect('bill_list')

    return render(
        request,
        'billing/bill_form.html',
        {'booking': booking}
    )


# =========================
# PAYMENTS
# =========================

@login_required
def payment_create(request, bill_id):
    bill = get_object_or_404(
        Bill,
        bill_id=bill_id
    )

    if request.method == 'POST':
        Payment.objects.create(
            bill=bill,
            payment_mode=request.POST.get(
                'payment_mode'
            ),
            amount=request.POST.get('amount'),
            transaction_id=request.POST.get(
                'transaction_id'
            ) or None,
        )

        paid_amount = sum(
            payment.amount
            for payment in bill.payments.all()
        )

        if paid_amount >= bill.total_amount:
            bill.payment_status = 'paid'
            bill.save()

        messages.success(
            request,
            'Payment recorded successfully.'
        )

        return redirect('bill_list')

    return render(
        request,
        'billing/payment_form.html',
        {'bill': bill}
    )