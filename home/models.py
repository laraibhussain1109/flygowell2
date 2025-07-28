from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver



# Create your models here.

class Package(models.Model):
    title = models.CharField(max_length=200)
    destination = models.CharField(max_length=100, default='Unknown')
    description = models.TextField()
    duration = models.CharField(max_length=50, blank=True, null=True)  # e.g., "5 Days / 4 Nights"
    image = models.ImageField(upload_to='packages/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
    
    bathrooms = models.PositiveIntegerField(default=1)
    beds = models.PositiveIntegerField(default=1)
    location_tag = models.CharField(
    max_length=100,
    blank=True,
    null=True,
    help_text="Custom location label like 'Near Beach', 'Mountain View', etc.")
    
    
    def __str__(self):
        return self.title
    



class Destination(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='destinations/')

    def __str__(self):
        return self.name

    @property
    def tour_count(self):
        from .models import Package
        return Package.objects.filter(destination__iexact=self.name).count()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)




class Video(models.Model):
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    embed_url = models.URLField(blank=True, null=True, help_text="Use this if you want to embed from Vimeo/YouTube.")
    is_active = models.BooleanField(default=True)  # Only show active video

    def __str__(self):
        return self.title




class Hotel(models.Model):
    ATTRACTION_CHOICES = [
        ('beach', 'Near Beach'),
        ('mountain', 'Near Mountain'),
        ('city', 'City Center'),
        ('desert', 'Near Desert'),
        ('forest', 'Near Forest'),
        ('lake', 'Near Lake'),
        ('none', 'No Specific Attraction'),
    ]

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    days = models.IntegerField()
    image = models.ImageField(upload_to='hotels/')
    bathrooms = models.IntegerField(default=1)
    beds = models.IntegerField(default=1)
    rating = models.IntegerField(default=5)  # 1 to 5 stars
    nearby_attraction = models.CharField(
        max_length=30,
        choices=ATTRACTION_CHOICES,
        default='none'
    )

    def __str__(self):  
        return self.name
    
    

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/')
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title



class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Required fields
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True)

    # Optional company info
    aadhar_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    company_address = models.TextField(blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create UserProfile when a new User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save UserProfile when User is saved.
    """
    instance.userprofile.save()




class Passenger(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passengers')

    # Passenger Details
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=100)

    # Travel Documents
    passport_number = models.CharField(max_length=30, blank=True, null=True)
    passport_issue = models.DateField(blank=True, null=True)
    passport_expiry = models.DateField(blank=True, null=True)
    aadhar_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} (Passenger of {self.user.username})"





class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    package = models.ForeignKey('Package', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'package')  # to prevent duplicate entries

    def __str__(self):
        return f"{self.user.username} - {self.package.title}"




class Testimonial(models.Model):
    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.IntegerField(default=5)  # 1 to 5 stars

    def __str__(self):
        return f"{self.full_name} ({self.position})"
