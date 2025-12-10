from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render,  get_object_or_404, resolve_url
from django.urls import  reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from .forms import  AppointmentForm, RegisterForm, ClientForm, ContactForm, ReviewForm, ServiceForm
from . models import  Appointment, Booking, Service, Client
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import  login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.views.decorators.http import require_http_methods


# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def service_list(request):
    return render(request, 'services.html' )

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.client = request.user
            appointment.save()

            # --- Email Notification ---
            subject = "Appointment Booked Successfully"
            message = f"Hi {request.user.username},\n\nYour appointment for {appointment.service.name} on {appointment.date} at {appointment.time} has been booked successfully. Status: {appointment.status}."
            recipient_list = [request.user.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=True)

            messages.success(request, "Appointment booked successfully! Notification sent.")
            return redirect('bookingsuccess')
    else:
        form = AppointmentForm()
    return render(request, 'book.html', {'form': form})


@login_required
def booking_success(request):
    return render(request, 'booksuccess.html')

# def book_success(request):
#     return render(request, "booksuccess.html")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('loginpage')
        # If form is invalid fall through to re-render with errors
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

@require_http_methods(["GET", "POST"])
def login_view(request):
    # If already logged in, send to book page
    if request.user.is_authenticated:
        return redirect('book')

    next_url = request.POST.get('next') or request.GET.get('next') or 'book'

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # AuthenticationForm has already validated credentials
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is inactive. Please contact support.")
                else:
                    auth_login(request, user)  # correct call: (request, user)
                    return redirect(resolve_url(next_url))
        # If we reach here credentials were invalid or form invalid
        messages.error(request, "Invalid login — incorrect username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form, "next": next_url})
  
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('homepage')

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

def staff_check(user):
    return user.is_active and user.is_staff

@user_passes_test(staff_check, login_url="/login/")
def admin_client_list(request):
    clients = Client.objects.all().order_by("-created_at")
    return render(request, "clientlist.html", {"clients": clients})


@user_passes_test(staff_check, login_url="/login/")
def add_personal_client(request):

    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)

            client.save()
            messages.success(request, "Added Successfully.")
            return redirect("list")
    else:
        form = ClientForm()

    return render(request, "clientform.html", {"form": form})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # saves to database
            messages.success(request, "Thank you! Your message has been received.")
            form = ContactForm()  # clear form
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form, "request": request})

@login_required(login_url='loginpage')
def allservices(request):
    return render(request, "allservices.html")

class StaffRequiredMixin(UserPassesTestMixin):
  
    def test_func(self):
        return self.request.user.is_staff
    
class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "clientlist.html"
    context_object_name = "clients"
    paginate_by = 10

    def get_queryset(self):
        qs = Client.objects.all().order_by("-created_at")

        q = self.request.GET.get("q")
        status = self.request.GET.get("status")

        if q:
            qs = qs.filter(
                first_name__icontains=q
            ) | qs.filter(
                last_name__icontains=q
            ) | qs.filter(
                email__icontains=q
            ) | qs.filter(
                phone__icontains=q
            )

        if status:
            qs = qs.filter(status=status)

        return qs

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "clientdetails.html"
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["review_form"] = ReviewForm()
        return context

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clientform.html"
    success_url = reverse_lazy("list")

    def form_valid(self, form):
     self.object = form.save() 
     messages.success(self.request, "Client added successfully.")
     return super().form_valid(form) 

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clientform.html"
    success_url = reverse_lazy("list")

    def form_valid(self, form):
        messages.success(self.request, "Client updated successfully.")
        return super().form_valid(form) 

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy("list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Client deleted successfully.")
        return super().delete(request, *args, **kwargs)


class ApproveClientView(LoginRequiredMixin, View):
    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        form = ReviewForm(request.POST)

        if form.is_valid():
            client.status = Client.STATUS_APPROVED
            client.review_notes = form.cleaned_data["review_notes"]
            client.reviewed_by = request.user
            client.reviewed_at = timezone.now()
            client.save()
            messages.success(request, "Client approved.")

        next_url =  reverse_lazy("list")
        return redirect(next_url)

class RejectClientView(LoginRequiredMixin, View):
    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk)
        form = ReviewForm(request.POST)

        if form.is_valid():
            client.status = Client.STATUS_REJECTED
            client.review_notes = form.cleaned_data["review_notes"]
            client.reviewed_by = request.user
            client.reviewed_at = timezone.now()
            client.save()
            messages.success(request, "Client rejected.")

        next_url = request.POST.get("next") or reverse_lazy("list")
        return redirect(next_url)
    
class ServiceListView(ListView):
    model = Service
    template_name = "servicelist.html"
    context_object_name = "services"

    # def get_queryset(self):
    #     return Service.objects.filter(is_active=True).order_by("name")


class ServiceCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "serviceform.html"
    success_url = reverse_lazy('serviceslist')

    def form_valid(self, form):
        messages.success(self.request, "Service added successfully.")
        return super().form_valid(form)


class ServiceUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):

    model = Service
    form_class = ServiceForm
    template_name = "serviceform.html"
    success_url = reverse_lazy('serviceslist')

    def form_valid(self, form):
        messages.success(self.request, "Service updated successfully.")
        return super().form_valid(form)
    

@login_required
def book(request):
    services = Service.objects.all()  # fetches all services from DB

    if request.method == "POST":
        # Get the selected services IDs from form
        selected_services_ids = request.POST.getlist("services")
        date = request.POST.get("date")
        time = request.POST.get("time")

        # Validation
        if not selected_services_ids:
            messages.error(request, "Please select at least one service.")
            return render(request, "book.html", {"services": services})

        if not date or not time:
            messages.error(request, "Please select date and time.")
            return render(request, "book.html", {"services": services})

        # Create booking entry
        booking = Booking.objects.create(
            client=request.user,
            date=date,
            time=time,
            status="Pending"
        )

        # Assign services to booking
        services_objects = Service.objects.filter(id__in=selected_services_ids)
        booking.services.set(services_objects)

        # Calculate total price
        booking.calculate_total()

        messages.success(request, "Booking created successfully!")
        return redirect("booksuccess")  # redirect to a success page

    return render(request, "book.html", {"services": services})


@user_passes_test(staff_check, login_url="/login/")
def booking_list(request):
    bookings = Appointment.objects.all().order_by('-date', '-time')  # Always assigned
    return render(request, 'bookinglist.html', {'bookings': bookings})

