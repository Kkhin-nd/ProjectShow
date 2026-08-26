from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class TourPackage(models.Model):
    # English Fields (Original)
    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    travel_style = models.CharField(max_length=100, default='Honeymoon Packages')

    # Burmese Fields (New)
    title_my = models.CharField(max_length=200, blank=True, null=True)
    tagline_my = models.CharField(max_length=255, blank=True, null=True)
    description_my = models.TextField(blank=True, null=True)
    duration_my = models.CharField(max_length=100, blank=True, null=True)

    # Pricing fields (MMK)
    price_2star = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    price_2star_my = models.CharField(max_length=100, blank=True, null=True) # မြန်မာလို
    
    price_3star = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    price_3star_my = models.CharField(max_length=100, blank=True, null=True) # မြန်မာလို
    
    price_4star = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    price_4star_my = models.CharField(max_length=100, blank=True, null=True) # မြန်မာလို
    
    price_5star = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    price_5star_my = models.CharField(max_length=100, blank=True, null=True) # မြန်မာလို
    
    price_includes = models.TextField(blank=True, null=True)
    price_includes_my = models.TextField(blank=True, null=True) # မြန်မာလို
    
    price_excludes = models.TextField(blank=True, null=True)
    price_excludes_my = models.TextField(blank=True, null=True) # မြန်မာလို

    duration = models.CharField(max_length=100)
    start_location = models.CharField(max_length=100, default='Yangon')
    start_location_my = models.CharField(max_length=100, blank=True, null=True)
    end_location = models.CharField(max_length=100, default='Yangon')
    end_location_my = models.CharField(max_length=100, blank=True, null=True)

    main_image = models.ImageField(upload_to='packages/')
    image_1 = models.ImageField(upload_to='packages/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='packages/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='packages/', blank=True, null=True)
    image_4 = models.ImageField(upload_to='packages/', blank=True, null=True)

    def __str__(self):
        return self.title


class Itinerary(models.Model):
    package = models.ForeignKey(TourPackage, related_name='itineraries', on_delete=models.CASCADE)
    day_number = models.IntegerField()
    title = models.TextField()  # English Title
    title_my = models.TextField(blank=True, null=True)  # Burmese Title
    description = models.TextField(blank=True, null=True) # English Desc
    description_my = models.TextField(blank=True, null=True) # Burmese Desc

    def __str__(self):
        return f'Day {self.day_number}: {self.title}'


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, null=True, blank=True)
    hotel_category = models.CharField(max_length=100, null=True, blank=True)
    travelers_count = models.IntegerField(default=1, null=True, blank=True)
    travel_date = models.DateField(null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    payment_method = models.CharField(max_length=100, null=True, blank=True)
    payment_option = models.CharField(max_length=100, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    pay_slip = models.ImageField(upload_to='payslips/', null=True, blank=True)
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.package}"


class TravelAgency(models.Model):
    name = models.CharField(max_length=255)
    name_my = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    description_my = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='agencies/')
    logo = models.ImageField(upload_to='agency_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    agency_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.subject}'


class ContactRequest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.email}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.first_name or self.user.username
    
class TourReview(models.Model):
    # သင့် project ၏ Tour/Package Model နာမည်နှင့် ForeignKey ချိတ်ပါ (ဥပမာ - TourPackage)
    package = models.ForeignKey('TourPackage', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5) # 1 မှ 5 ထိ Rating ပေးရန်
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating} Stars"
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5) # 1 မှ 5 အထိ rating ပေးရန်
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.rating} Stars"
    
class CustomTripPlan(models.Model):
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    travel_style = models.CharField(max_length=100, blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    destination = models.CharField(max_length=100, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    budget = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.destination}"
    
