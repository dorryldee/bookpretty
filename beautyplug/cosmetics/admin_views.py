from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Appointment
from django.core.mail import send_mail

@staff_member_required
def admin_bookings(request):
    bookings = Appointment.objects.all().order_by('-date', '-time')
    return render(request, 'bookings.html', {'bookings': bookings})


@staff_member_required
def approve_booking(request, id):
    booking = get_object_or_404(Appointment, id=id)
    booking.status = 'Approved'
    booking.save()

    # Send email to client
    subject = "Appointment Approved"
    message = f"Hi {booking.client.username},\n\nYour appointment for {booking.service.name} on {booking.date} at {booking.time} has been approved."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [booking.client.email], fail_silently=True)

    return redirect('admin_bookings')


@staff_member_required
def reject_booking(request, id):
    booking = get_object_or_404(Appointment, id=id)
    booking.status = 'Rejected'
    booking.save()

    # Send email to client
    subject = "Appointment Rejected"
    message = f"Hi {booking.client.username},\n\nYour appointment for {booking.service.name} on {booking.date} at {booking.time} has been rejected."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [booking.client.email], fail_silently=True)

    return redirect('admin_bookings')