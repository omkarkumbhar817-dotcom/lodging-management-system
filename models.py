from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('receptionist', 'Receptionist'),
        ('staff', 'Staff'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff'
    )

    phone = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

from django.db import models
class Guest(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    id_proof = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    identity_number = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name    

from django.db import models


class RoomType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    tariff = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Room(models.Model):

    STATUS_CHOICES = (
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('occupied', 'Occupied'),
        ('housekeeping', 'Housekeeping'),
        ('maintenance', 'Maintenance'),
    )

    room_id = models.AutoField(primary_key=True)
    room_number = models.CharField(max_length=20, unique=True)

    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name='rooms'
    )

    floor_number = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )

    def __str__(self):
        return f"Room {self.room_number}"

from django.db import models
from app.models import Guest
from app.models import Room


class Booking(models.Model):

    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    booking_id = models.AutoField(primary_key=True)

    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    check_in_date = models.DateField()
    check_out_date = models.DateField()

    booking_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )

    def __str__(self):
        return f"Booking #{self.booking_id}"
    from django.db import models
from app.models import Guest
from app.models import Room
from app.models import Booking


class CheckIn(models.Model):
    checkin_id = models.AutoField(primary_key=True)

    booking = models.OneToOneField(
        Booking,
        on_delete=models.PROTECT,
        related_name='checkin'
    )

    guest = models.ForeignKey(
        Guest,
        on_delete=models.PROTECT,
        related_name='checkins'
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='checkins'
    )

    checkin_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Check-in #{self.checkin_id}"


class CheckOut(models.Model):
    checkout_id = models.AutoField(primary_key=True)

    checkin = models.OneToOneField(
        CheckIn,
        on_delete=models.PROTECT,
        related_name='checkout'
    )

    checkout_datetime = models.DateTimeField(auto_now_add=True)

    number_of_nights = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Check-out #{self.checkout_id}"
from django.db import models
from app.models import Booking


class Service(models.Model):
    service_id = models.AutoField(primary_key=True)

    service_name = models.CharField(max_length=100)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.service_name


class Bill(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    )

    bill_id = models.AutoField(primary_key=True)

    booking = models.OneToOneField(
        Booking,
        on_delete=models.PROTECT,
        related_name='bill'
    )

    number_of_nights = models.PositiveIntegerField()

    room_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    service_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    bill_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.bill_id}"


class Payment(models.Model):

    PAYMENT_MODE_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
        ('upi', 'UPI'),
    )

    payment_id = models.AutoField(primary_key=True)

    bill = models.ForeignKey(
        Bill,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateTimeField(auto_now_add=True)

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Payment #{self.payment_id}"