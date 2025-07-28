from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.models import User
from .forms import ContactForm
from .models import Video
from .models import Hotel
from .models import Blog
from .utils import send_otp_email, generate_otp
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from .models import Testimonial
import random
from .models import UserProfile, Passenger, CartItem, Package, Destination
from .forms import UserProfileForm, PassengerForm, CustomUserCreationForm
from django.conf import settings





# Create your views here.


def index(request):
    packages = Package.objects.all()
    destinations = sorted(Destination.objects.all(), key=lambda d: d.tour_count, reverse=True)
    video = Video.objects.filter(is_active=True).first()
    testimonials = Testimonial.objects.all()
    blogs = Blog.objects.order_by('-created_at')[:3]

    return render(request, 'index.html', {
        'packages': packages,
        'destinations': destinations,
        'video': video,
        'testimonials': testimonials,
        'blogs': blogs,
    })

def about(request):
    testimonials = Testimonial.objects.all()
    return render(request, 'about.html', {
        'testimonials': testimonials,
    })
    
    
    
    
    

def signup(request):
    # Initial Flags
    email_verified = False
    otp_verified = False
    verified_email = request.session.get('verified_email', '')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send_otp':
            email = request.POST.get('email')   
            otp = generate_otp()
            # Store email and OTP in session
            request.session['temp_email'] = email
            request.session['temp_otp'] = otp
            # Send the OTP
            send_otp_email(email, otp)
            messages.info(request, "OTP sent to your email.")

            # Show OTP input form
            email_verified = True
            otp_verified = False
            return render(request, 'signup.html', {
                'email_verified': email_verified,
                'otp_verified': otp_verified,
                'verified_email': email,
            })

        elif action == 'verify_otp':
            input_otp = request.POST.get('otp')
            if input_otp == request.session.get('temp_otp'):
                request.session['verified_email'] = request.session.get('temp_email')
                messages.success(request, "Email verified! Complete your signup.")
                email_verified = True
                otp_verified = True
            else:
                messages.error(request, "Incorrect OTP. Please try again.")
                return render(request, 'signup.html', {
                    'email_verified': False,
                })

            return render(request, 'signup.html', {
                'email_verified': email_verified,
                'otp_verified': otp_verified,
                'verified_email': request.session['temp_email'],
            })

        elif action == 'submit_signup':
            username = request.POST.get('username')
            phone = request.POST.get('phone')
            password = request.POST.get('password')
            confirm = request.POST.get('password_confirm')
            email = request.session.get('verified_email')

            # --- Your existing validations here ---
            # if password != confirm: ...
            # if User.objects.filter(username=username).exists(): ...
            # if UserProfile.objects.filter(phone=phone).exists(): ...

            # 1) Create the User (this fires your post_save signal)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # 2) Fetch & update the existing UserProfile
            profile = user.userprofile
            profile.phone = phone
            profile.full_name = username
            profile.is_verified = True
            profile.save()

            # 3) Clear temp session data
            for key in ('temp_email', 'temp_otp', 'verified_email'):
                request.session.pop(key, None)

            # 4) Success and redirect
            messages.success(request, "Signup successful! You can now login.")
            return redirect('login')

    # ─────────────────────────────────────────────────────────
    # DEFAULT: for GET, or POST with no/unknown action,
    # always render the signup form with initial flags:
    return render(request, 'signup.html', {
        'email_verified': False,
        'otp_verified': False,
    })

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        messages.success(self.request, "Login successful!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('index')  # or another named URL like 'dashboard'


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have logged out successfully.")
        return super().dispatch(request, *args, **kwargs)



# Blog list view
def blog_list(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'blog.html', {'blogs': blogs})


# Single blog view
def blog_single(request, id):
    blog = get_object_or_404(Blog, id=id)
    return render(request, 'blog_single.html', {'blog': blog})

    
    
def destination(request):
    packages = Package.objects.all()  # This is REQUIRED
    return render(request, 'destination.html', {
        'packages': packages
    })
    


def hotel(request):
    hotels = Hotel.objects.all()
    return render(request, 'hotel.html', {'hotels': hotels})




def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact')  # or show a success message
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})





@login_required
def profile_view(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    cart_items = CartItem.objects.filter(user=user).select_related('package')

    PassengerFormSet = modelformset_factory(
        Passenger,
        form=PassengerForm,
        extra=1,
        can_delete=True
    )

    form = UserProfileForm(instance=profile)
    formset = PassengerFormSet(queryset=user.passengers.all(), prefix='p')

    if request.method == 'POST':
        if 'save_profile' in request.POST:
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Your profile has been updated.")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors in your profile.")

        elif 'save_passengers' in request.POST:
            formset = PassengerFormSet(request.POST, queryset=user.passengers.all(), prefix='p')
            if formset.is_valid():
                try:
                    passengers = formset.save(commit=False)
                    for passenger in passengers:
                        passenger.user = user
                        passenger.save()

                    for obj in formset.deleted_objects:
                        obj.delete()

                    formset.save()  # ← important
                    messages.success(request, "Travellers updated successfully.")
                    return redirect('profile')
                except Exception as e:
                    messages.error(request, f"Error saving travellers: {str(e)}")
            else:
                messages.error(request, "Please correct the errors in traveller information.")
                print("Formset errors:", formset.errors)
                print("Non-form errors:", formset.non_form_errors())

    return render(request, 'profile.html', {
        'form': form,
        'formset': formset,
        'profile': profile,
        'cart_items': cart_items,
    })

    
 
    

def search_packages(request):
    destination = request.GET.get('destination')
    price_range = request.GET.get('price_range')
    
    packages = Package.objects.all()

    if destination:
        packages = packages.filter(destination__icontains=destination)
    
    if price_range:
        try:
            min_p, max_p = map(int, price_range.split('-'))
            packages = packages.filter(price__gte=min_p, price__lte=max_p)  # ✅ use `packages`, not `qs`
        except ValueError:
            pass  # ignore bad input

    return render(request, 'search_results.html', {'packages': packages})






@login_required
def add_to_cart(request, package_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to log in to add packages.")
        return redirect('login')
    
    package = get_object_or_404(Package, id=package_id)
    CartItem.objects.get_or_create(user=request.user, package=package)
    messages.success(request, f"'{package.title}' has been added to your packages.")
    return redirect('profile')


@login_required
def remove_from_cart(request, package_id):
    item = get_object_or_404(CartItem, user=request.user, package_id=package_id)
    item.delete()
    messages.success(request, "Package removed from My Packages.")
    return redirect('profile')





def generate_otp():
    return str(random.randint(100000, 999999))

def forgot_password(request):
    step = "email"  # default

    if request.method == "POST":
        action = request.POST.get('action')
        email = request.session.get('reset_email')

        if not email and request.POST.get('email'):
            email = request.POST.get('email')
            request.session['reset_email'] = email

        if not email:
            messages.error(request, "Email is required.")
            return render(request, 'forgot_password.html', {'step': 'email'})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return render(request, 'forgot_password.html', {'step': 'email'})

        if action == 'reset':
            input_otp = request.POST.get('otp')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if input_otp != request.session.get('reset_otp'):
                messages.error(request, "Invalid OTP.")
                return render(request, 'forgot_password.html', {'step': 'otp'})

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'forgot_password.html', {'step': 'otp'})

            user.set_password(new_password)
            user.save()

            # Clear session data
            request.session.pop('reset_email', None)
            request.session.pop('reset_otp', None)

            messages.success(request, "Password reset successful! You can now log in.")
            return redirect('login')

        else:  # Send or resend OTP
            otp = generate_otp()
            request.session['reset_otp'] = otp

            send_mail(
                subject="Your OTP for Password Reset",
                message=f"Your OTP is: {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "OTP has been sent to your email.")
            return render(request, 'forgot_password.html', {'step': 'otp'})

    return render(request, 'forgot_password.html', {'step': 'email'})