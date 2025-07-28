from django.contrib import admin
from .models import Package
from .models import Destination
from .models import Video
from .models import Hotel
from .models import Blog
from .models import ContactMessage
from .models import UserProfile, Passenger
from .models import Testimonial


# Register your models here.

admin.site.register(Destination)
admin.site.register(Video)
admin.site.register(Blog)
admin.site.register(ContactMessage)
admin.site.register(Testimonial)

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'price', 'days', 'rating']
    
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone', 'aadhar_number', 'company_name', 'designation')
    list_filter = ('company_name',)  # Use only fields that still exist


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'age', 'nationality', 'aadhar_number')
    list_filter = ('gender', 'nationality')
    
    
@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'price', 'location_tag')
    search_fields = ('title', 'destination', 'location_tag')
    list_filter = ('destination',)
    fields = ('title', 'destination', 'description', 'duration', 'location_tag', 'image', 'price')


