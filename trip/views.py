from django.conf import settings
import os
from django.utils.text import slugify
from urllib.parse import unquote
from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from .models import TourPackage, Booking, Itinerary, Review, UserProfile
from .models import TravelAgency, ContactMessage
from .forms import TravelAgencyForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from .models import TourPackage
import requests
from django.http import Http404
from google import genai
import traceback

def home(request):
    packages = TourPackage.objects.all().order_by('-id')[:4]
    context = {'packages': packages}
    return render(request, 'trip/home.html', context)

def travel_styles(request):
    packages = TourPackage.objects.all()
    
    selected_styles = request.GET.getlist('style')
    if selected_styles:
        packages = packages.filter(travel_style__in=selected_styles)
        
    sort_by = request.GET.get('sort', 'popular')
    if sort_by == 'title_az':
        packages = packages.order_by('title')
    elif sort_by == 'title_za':
        packages = packages.order_by('-title')
    elif sort_by == 'price_low':
        packages = packages.order_by('price_2star')
    elif sort_by == 'price_high':
        packages = packages.order_by('-price_2star')
    elif sort_by == 'duration_short':
        packages = packages.order_by('duration')
    elif sort_by == 'duration_long':
        packages = packages.order_by('-duration')
    else:
        packages = packages.order_by('-id')

    context = {
        'packages': packages,
    }
    return render(request, 'trip/travel_styles.html', context)

def travel_agents(request):
    agencies = TravelAgency.objects.all().order_by('-id')
    context = {'agencies': agencies}
    return render(request, 'trip/travel_agencies.html', context)

def seasonal_trips(request):
    return render(request, 'trip/season.html')

def plan_trip_form(request):
    return render(request, 'trip/home.html')

def tours_list(request):
    style_query = request.GET.get('style', '')
    if style_query:
        packages = TourPackage.objects.filter(travel_style__icontains=style_query)
    else:
        packages = TourPackage.objects.all()
    context = {'packages': packages}
    return render(request, 'trip/tours.html', context)

def plan_trip_view(request):
    return render(request, 'trip/plan_trip.html')

def package_detail(request, pk):
    # pk က ဂဏန်း (ID) ဟုတ်မဟုတ် စစ်မယ်
    if str(pk).isdigit():
        package = get_object_or_404(TourPackage, pk=pk)
    else:
        clean_slug = unquote(pk).strip().lower()
        
        # ၁။ ပထမဆုံး slugify လုပ်ပြီး တိုက်စစ်မည်
        package = None
        for p in TourPackage.objects.all():
            if slugify(p.title) == clean_slug:
                package = p
                break
        
        # ၂။ မတွေ့သေးရင် hyphen တွေကို space ပြောင်းပြီး icontains နဲ့ ရှာမည်
        if not package:
            search_query = clean_slug.replace('-', ' ')
            package = TourPackage.objects.filter(title__icontains=search_query).first()

        # ၃။ အကယ်၍ ဒါတောင် မတွေ့သေးရင် စာလုံးအစ (ဥပမာ popa) ပါတာနဲ့တင် အရင်ဆုံး ရှာပေးမည်
        if not package:
            first_word = clean_slug.split('-')[0]
            package = TourPackage.objects.filter(title__icontains=first_word).first()

        if not package:
            raise Http404("Tour package not found")

    itineraries = package.itineraries.all()
    
    if request.method == 'POST':
        hotel_category = request.POST.get('hotel_category')
        travelers_count = request.POST.get('travelers_count', 1)
        travel_date = request.POST.get('travel_date')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        payment_method = request.POST.get('payment_method')
        payment_option = request.POST.get('payment_option')
        transaction_id = request.POST.get('transaction_id')
        pay_slip = request.FILES.get('pay_slip')
        
        Booking.objects.create(
            package=package,
            user=request.user if request.user.is_authenticated else None,
            email=email,
            hotel_category=hotel_category,
            travelers_count=travelers_count,
            travel_date=travel_date,
            full_name=full_name,
            phone_number=phone_number,
            payment_method=payment_method,
            payment_option=payment_option,
            transaction_id=transaction_id,
            pay_slip=pay_slip
        )
        messages.success(request, "Booking submitted successfully!")
        return redirect('package_detail', pk=pk)

    context = {
        'package': package,
        'itineraries': itineraries
    }
    return render(request, 'trip/package_detail.html', context)

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        agency_name = request.POST.get('agency_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            agency_name=agency_name,
            phone=phone,
            email=email,
            subject=subject,
            message=message
        )
        return redirect('contact_us')
        
    return render(request, 'trip/contact.html')

def about_view(request):
    return render(request, 'trip/about.html')

# --- ADMIN VIEWS ---

from .models import TourPackage, Booking, Review, User, CustomTripPlan # (သင့်ရဲ့ Model အမှန်ကို ထည့်ပါ)

def admin_dashboard(request):
    total_packages = TourPackage.objects.count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status__iexact='Pending').count()
    registered_users = User.objects.count() 
    total_reviews = Review.objects.count()

    # Recent Bookings ဇယားအတွက် Pending ဖြစ်နေသော bookings များကို `recent_bookings` နာမည်ဖြင့် ပို့ရန်
    recent_bookings = Booking.objects.filter(status__iexact='Pending').order_by('-id')

    # CustomTripPlan ထဲမှ Pending ဖြစ်နေသော Requests များကို ယူခြင်း
    custom_plans = CustomTripPlan.objects.filter(status__iexact='Pending').order_by('-id') 

    context = {
        'total_packages': total_packages,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'registered_users': registered_users,
        'total_reviews': total_reviews,
        'recent_bookings': recent_bookings, # template ထဲသုံးမည့် variable
        'custom_plans': custom_plans,
    }
    return render(request, 'trip/admin_dashboard.html', context)
def admin_packages(request):
    query = request.GET.get('q', '').strip()
    packages = TourPackage.objects.all().order_by('-id')

    if query and query != 'All Styles':
        packages = packages.filter(
            models.Q(title__icontains=query) | 
            models.Q(tagline__icontains=query) | 
            models.Q(description__icontains=query) |
            models.Q(travel_style__icontains=query)
        )

    context = {
        'packages': packages,
    }
    return render(request, 'trip/admin_packages.html', context)

def admin_bookings(request):
    bookings = Booking.objects.all().order_by('-id')
    context = {'bookings': bookings}
    return render(request, 'trip/admin_bookings.html', context)

def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    context = {'users': users}
    return render(request, 'trip/admin_users.html', context)

def admin_reviews_view(request):
    reviews = Review.objects.all().order_by('-created_at')
    context = {'reviews': reviews}
    return render(request, 'trip/admin_reviews.html', context)

@login_required
def admin_delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('admin_reviews')

def create_travel_package_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        tagline = request.POST.get('tagline')
        description = request.POST.get('description')
        travel_style = request.POST.get('travel_style', 'Honeymoon Special')
        
        price_2star = request.POST.get('price_2star', 0)
        price_3star = request.POST.get('price_3star', 0)
        price_4star = request.POST.get('price_4star', 0)
        price_5star = request.POST.get('price_5star', 0)
        
        duration = request.POST.get('duration')
        start_location = request.POST.get('start_location', 'Yangon')
        end_location = request.POST.get('end_location', 'Yangon')

        main_image = request.FILES.get('main_image')
        image_1 = request.FILES.get('image_1')
        image_2 = request.FILES.get('image_2')
        image_3 = request.FILES.get('image_3')
        image_4 = request.FILES.get('image_4')

        package = TourPackage.objects.create(
            title=title,
            tagline=tagline,
            description=description,
            travel_style=travel_style,
            price_2star=price_2star,
            price_3star=price_3star,
            price_4star=price_4star,
            price_5star=price_5star,
            duration=duration,
            start_location=start_location,
            end_location=end_location,
            main_image=main_image,
            image_1=image_1,
            image_2=image_2,
            image_3=image_3,
            image_4=image_4,
        )

        i = 0
        while True:
            day_title = request.POST.get(f'itinerary_title_{i}')
            if not day_title:
                break 

            day_number = request.POST.get(f'itinerary_day_{i}', i + 1)

            Itinerary.objects.create(
                package=package,
                day_number=day_number,
                title=day_title,
                description="",
            )
            i += 1

        return redirect('admin_packages')

    return render(request, 'trip/admin_package_create.html')

def admin_package_edit(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)

    if request.method == 'POST':
        # Travel Style & Location Info
        package.travel_style = request.POST.get('travel_style')
        package.duration = request.POST.get('duration')
        package.duration_my = request.POST.get('duration_my')
        
        package.start_location = request.POST.get('start_location')
        package.start_location_my = request.POST.get('start_location_my') # <-- ဒီနေရာလေး ထည့်ပေးရန်
        
        package.end_location = request.POST.get('end_location')
        package.end_location_my = request.POST.get('end_location_my')   # <-- ဒီနေရာလေး ထည့်ပေးရန်

        # English Fields
        package.title = request.POST.get('title')
        package.tagline = request.POST.get('tagline')
        package.description = request.POST.get('description')
        package.price_includes = request.POST.get('price_includes')
        package.price_excludes = request.POST.get('price_excludes')

        # Myanmar Fields
        package.title_my = request.POST.get('title_my')
        package.tagline_my = request.POST.get('tagline_my')
        package.description_my = request.POST.get('description_my')
        package.price_includes_my = request.POST.get('price_includes_my')
        package.price_excludes_my = request.POST.get('price_excludes_my')

        # Hotel Pricing
        package.price_2star = request.POST.get('price_2star') or 0
        package.price_2star_my = request.POST.get('price_2star_my')
        package.price_3star = request.POST.get('price_3star') or 0
        package.price_3star_my = request.POST.get('price_3star_my')
        package.price_4star = request.POST.get('price_4star') or 0
        package.price_4star_my = request.POST.get('price_4star_my')
        package.price_5star = request.POST.get('price_5star') or 0
        package.price_5star_my = request.POST.get('price_5star_my')

        # Image Uploads
        if 'main_image' in request.FILES:
            package.main_image = request.FILES['main_image']
        if 'image_1' in request.FILES:
            package.image_1 = request.FILES['image_1']
        if 'image_2' in request.FILES:
            package.image_2 = request.FILES['image_2']
        if 'image_3' in request.FILES:
            package.image_3 = request.FILES['image_3']
        if 'image_4' in request.FILES:
            package.image_4 = request.FILES['image_4']

        package.save()

        # --- ITINERARIES UPDATE ---
        package.itineraries.all().delete()

        i = 0
        while True:
            day_title = request.POST.get(f'itinerary_title_{i}')
            if not day_title:
                break

            day_number = request.POST.get(f'itinerary_day_{i}', i + 1)
            day_title_my = request.POST.get(f'itinerary_title_my_{i}', '')
            day_description = request.POST.get(f'itinerary_description_{i}', '')
            day_description_my = request.POST.get(f'itinerary_description_my_{i}', '')

            Itinerary.objects.create(
                package=package,
                day_number=day_number,
                title=day_title,
                title_my=day_title_my,
                description=day_description,
                description_my=day_description_my,
            )
            i += 1

        return redirect('admin_packages')

    context = {'package': package}
    return render(request, 'trip/admin_package_edit.html', context)

def admin_package_delete(request, pk):
    package = get_object_or_404(TourPackage, pk=pk)
    package.delete()
    return redirect('admin_packages')

def admin_agencies(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        logo = request.FILES.get('logo')

        TravelAgency.objects.create(
            name=name,
            description=description,
            image=image,
            logo=logo
        )
        return redirect('admin_agencies')

    agencies = TravelAgency.objects.all().order_by('-id')
    context = {'agencies': agencies}
    return render(request, 'trip/admin_agencies.html', context)

def admin_edit_agency(request, pk):
    agency = get_object_or_404(TravelAgency, pk=pk)
    
    if request.method == 'POST':
        agency.name = request.POST.get('name')
        agency.name_my = request.POST.get('name_my')
        agency.description = request.POST.get('description')
        agency.description_my = request.POST.get('description_my')
        
        if 'image' in request.FILES:
            agency.image = request.FILES['image']
        if 'logo' in request.FILES:
            agency.logo = request.FILES['logo']
            
        agency.save()
        return redirect('admin_agencies')

    return render(request, 'trip/admin_edit_agency.html', {'agency': agency})

def admin_delete_agency(request, pk):
    agency = get_object_or_404(TravelAgency, pk=pk)
    agency.delete()
    return redirect('admin_agencies')

# --- AUTH & USER VIEWS ---

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'User with this email does not exist.')
            
    return redirect('home')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        email = request.POST.get('email')
        confirm_email = request.POST.get('confirm_email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        address = request.POST.get('address')
        
        if email != confirm_email:
            messages.error(request, 'Emails do not match.')
            return redirect('home')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('home')
            
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        
        UserProfile.objects.create(
            user=user,
            phone=phone,
            age=age or None,
            address=address
        )
        
        login(request, user)
        messages.success(request, 'Account created successfully! Welcome to Myanmar Travel.')
        return redirect('home')
        
    return redirect('home')

def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
            user_profile.save()
            messages.success(request, "Profile picture updated successfully!")
            return redirect('profile')

        if request.POST.get('remove_picture') == 'true':
            if user_profile.profile_picture:
                user_profile.profile_picture.delete(save=False)
                user_profile.profile_picture = None
                user_profile.save()
                messages.success(request, "Profile picture removed successfully!")
            return redirect('profile')

        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        
        if first_name and first_name.strip():
            request.user.first_name = first_name.strip()
            
        if email and email.strip():
            request.user.email = email.strip()
            
        request.user.save() 

        user_profile.phone = request.POST.get('phone', user_profile.phone)
        user_profile.age = request.POST.get('age') or None
        user_profile.address = request.POST.get('address', user_profile.address)
        user_profile.save()

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password:
            if new_password == confirm_password:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Password updated successfully! Please log in again.")
                return redirect('login')
            else:
                messages.error(request, "New passwords do not match.")
                return redirect('profile')

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    bookings = Booking.objects.filter(email=request.user.email).order_by('-id')

    context = {
        'user_profile': user_profile,
        'bookings': bookings,  
    }
    return render(request, 'trip/profile.html', context)

def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'Confirmed'
    booking.save()
    return redirect('admin_bookings')  

def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'Cancelled'
    booking.save()
    return redirect('admin_bookings')

def complete_trip(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'Completed'
    booking.save()
    return redirect('admin_bookings')

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status in ['Pending', 'Confirmed']:
        booking.status = 'Cancelled'
        booking.save()
        messages.warning(request, "ခရီးစဉ်ကို ဖျက်သိမ်းလိုက်ပါပြီ။ စည်းကမ်းချက်အရ total price ၏ 20% ဆုံးရှုံးမည်ဖြစ်ပါသည်။")
        
    return redirect('profile')

def reviews_view(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if request.user.is_authenticated:
            Review.objects.create(
                user=request.user,
                rating=rating,
                comment=comment
            )
            return redirect('reviews')
            
    reviews = Review.objects.all().order_by('-created_at')
    context = {'reviews': reviews}
    return render(request, 'trip/reviews.html', context)


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        review.rating = request.POST.get('rating')
        review.comment = request.POST.get('comment')
        review.save()
        return redirect('reviews')  # Reviews စာမျက်နှာသို့ ပြန်သွားရန်
        
    return render(request, 'trip/edit_review.html', {'review': review})

 # သင့်ရဲ့ Package Model နာမည်အတိုင်း ထည့်ပါ

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('reviews')


import re
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TourPackage, Booking

def plan_trip_view(request):
    packages = TourPackage.objects.all()  
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number') 
        travel_style = request.POST.get('travel_style')
        place = request.POST.get('place')
        destination = request.POST.get('destination')
        duration = request.POST.get('duration')
        travelers_raw = request.POST.get('travelers') 
        budget = request.POST.get('budget')
        
        # Booking နဲ့ မရောဘဲ Plan My Trip အတွက် CustomTripPlan ထဲသို့ သီးသန့်သိမ်းဆည်းခြင်း
        CustomTripPlan.objects.create(
            full_name=name,
            email=email,
            phone_number=phone_number,
            travel_style=travel_style,
            place=place,
            destination=destination,
            duration=duration,
            budget=budget,
            status='Pending'
        )
        
        # AJAX Request ဖြစ်ပါက JSON ပြန်ရန်
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        return redirect('home')

    context = {
        'packages': packages,
    }
    return render(request, 'trip/plan_trip.html', context)

def trip_plan_management_list_view(request):
    approved_plans = CustomTripPlan.objects.filter(status__iexact='Approved').order_by('-id')
    
    context = {
        'approved_plans': approved_plans,
    }
    return render(request, 'trip/trip_plan_management.html', context)

def approve_trip_plan(request, plan_id):
    plan = get_object_or_404(CustomTripPlan, id=plan_id)
    plan.status = 'Approved'
    plan.save()
    return redirect('trip_plan_management_list')

def terms_view(request):
    return render(request, 'trip/terms.html')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

API_KEYS = [
    os.getenv("OPENROUTER_API_KEY_1"),
    os.getenv("OPENROUTER_API_KEY_2"),
    os.getenv("OPENROUTER_API_KEY_3"),
    os.getenv("OPENROUTER_API_KEY_4"),
    os.getenv("OPENROUTER_API_KEY_5"),
    os.getenv("OPENROUTER_API_KEY_6"),
    os.getenv("OPENROUTER_API_KEY_7"),
    os.getenv("OPENROUTER_API_KEY_8"),
    os.getenv("OPENROUTER_API_KEY_9"),
    os.getenv("OPENROUTER_API_KEY_10"),
    os.getenv("OPENROUTER_API_KEY_11"),
    os.getenv("OPENROUTER_API_KEY_12"),
    os.getenv("OPENROUTER_API_KEY_13"),
    os.getenv("OPENROUTER_API_KEY_14"),
    os.getenv("OPENROUTER_API_KEY_15"),
    os.getenv("OPENROUTER_API_KEY_16"),
    os.getenv("OPENROUTER_API_KEY_17"),
    os.getenv("OPENROUTER_API_KEY_18"),
    os.getenv("OPENROUTER_API_KEY_19"),
    os.getenv("OPENROUTER_API_KEY_20"),
]

# None ဖြစ်နေသော (သို့မဟုတ် မထည့်ရသေးသော) Key များကို ဖယ်ထုတ်ရန်
API_KEYS = [key for key in API_KEYS if key]

@csrf_exempt
def ai_chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Frontend က ပို့လိုက်သော chatHistory (list) ကို ရယူခြင်း
            messages_from_frontend = data.get('messages', [])
            
            # တစ်ခါတလေ တစ်ကြောင်းချင်း ပို့လာခဲ့ရင် backup အနေနဲ့ ဖမ်းရန်
            if not messages_from_frontend and 'message' in data:
                messages_from_frontend = [{"role": "user", "content": data.get('message')}]

            # နောက်ဆုံး အသုံးပြုသူ မေးလိုက်တဲ့ မေးခွန်းကို ထုတ်ယူရန်
            user_latest_message = ""
            if messages_from_frontend:
                user_latest_message = messages_from_frontend[-1].get('content', '')

            # --- ခရီးသွား Knowledge ဖိုင်ဖတ်ရန် ---
            knowledge_path = os.path.join(settings.BASE_DIR, 'travel_knowledge.json')
            project_knowledge = ""
            if os.path.exists(knowledge_path):
                with open(knowledge_path, 'r', encoding='utf-8') as f:
                    project_knowledge = f.read()

            # --- System Prompt တည်ဆောက်ခြင်း (စာပိုဒ်နှင့် လင့်ခ်ပါဝင်စေရန် ပြင်ဆင်ထားသည်) ---
            # --- System Prompt တည်ဆောက်ခြင်း (Travel Style လင့်ခ်သာ ပြသရန်) ---
            system_prompt = f"""
CRITICAL RULE: DO NOT output any internal thoughts, reasoning, or planning process. Directly output the final response in Myanmar language. Never show "The user is asking..." or any thinking steps.
CRITICAL RULE: NEVER use markdown asterisks (*), bold symbols (**), hash symbols (#) in your output. Write in clean plain text paragraphs.

သင်သည် ဖော်ရွေပြီး အသုံးဝင်သော မြန်မာခရီးသွား ဘော့တ် (Myanmar Travel Bot) ဖြစ်ပါသည်။

တင်းကြပ်သော ဖြေဆိုပုံ စည်းမျဉ်းများ (CRITICAL RULES):
၁။ အသုံးပြုသူက ခရီးသွားစတိုင် (Travel Style) အကြောင်း မေးမြန်းလာပါက Beach & Island, Cultural & Heritage, Nature & Adventure, Luxury Escape, Family Holiday, Honeymoon Special, Pilgrimage Tour ဟူသော စတိုင် ၇ မျိုးကို ဖော်ပြပါ။ (လင့်ခ် လုံးဝမထည့်ရပါ)။
၂။ အသုံးပြုသူက Tour Packages များအကြောင်း မေးမြန်းလာပါက ရှိပြီးသား packages များကို ဖော်ပြပေးပါ။
၃။ အသုံးပြုသူက မိုးရာသီ (သို့မဟုတ် Seasonal) အတွက် သွားသင့်သော ပက်ကေ့ဂျ်များအကြောင်း မေးမြန်းလာပါက သက်ဆိုင်ရာ packages များကို ဖော်ပြပေးပါ။
၄။ အသုံးပြုသူက Package တစ်ခုခုကို ရွေးချယ်လာပါက သို့မဟုတ် Package အသေးစိတ်ကို မေးမြန်းလာပါက ထို package ၏ အမည်၊ အကျဉ်းချုပ်နှင့် ဈေးနှုန်းတို့ကို ဖော်ပြပေးပြီး /package/ID/ (ဥပမာ - /package/52/ ကဲ့သို့ Knowledge ဖိုင်ထဲတွင် ဖော်ပြထားသော သက်ဆိုင်ရာ ID နံပါတ်) ဖြင့် လင့်ခ်ချိတ်ပေးပါ။
၅။ ခရီးသွားနှင့် မဆိုင်သော မေးခွန်းများကို လုံးဝမဖြေပါ과။ စာကြောင်းများကို သပ်ရပ်စွာ ခွဲခြားရေးသားပါ။
၆။Popular destinations အကြောင်းမေးရင် name တွေက်ိဘဲ ပြောပြပါ user က တစ်ခုကို ရွေးလိုက်မှ details ပြောပြပါ။
၇။အသုံးပြုသူမှ ကိုယ်ပိုင်သီးသန့် (Private Tour) သွားလိုကြောင်း သို့မဟုတ် Custom Trip လုပ်လိုကြောင်း မေးမြန်းလာပါက အောက်ပါအတိုင်း ဖြေကြားပေးပါ:
"ဟုတ်ကဲ့ပါရှင့်။ ကိုယ်ပိုင်သီးသန့် (Private Tour) အနေနဲ့ မိသားစု၊ မိတ်ဆွေသူငယ်ချင်း ရင်းနှီးသူတွေချည်းပဲ သီးသန့်သွားရောက်ချင်တယ်ဆိုရင် ကျွန်တော်တို့ စီစဉ်ဆောင်ရွက်ပေးပါတယ်ရှင့်။ ခရီးစဉ်အသေးစိတ်၊ သွားရောက်မည့်ရက်နဲ့ လူဦးရေစာရင်းတွေအပေါ်မူတည်ပြီး လိုအပ်တာတွေကို စိတ်ကြိုက်ညှိနှိုင်း ဆောင်ရွက်ပေးနိုင်ပါတယ်။ လူကြီးမင်းတို့အနေနဲ့ Custom Trip တစ်ခုကို ဖန်တီးချင်တယ်ဆိုရင် [ဤနေရာကိုနှိပ်ပါ](/plan-trip/) ပြီးတော့ ဆက်သွယ်နိုင်ပါတယ်ရှင့်။"
၈။အသုံးပြုသူမှ ဘိုကင်မှတ်တမ်း (Booking History) တွေကို ဘယ်မှာ ပြန်ကြည့်ရမလဲ မေးမြန်းလာပါက အောက်ပါအတိုင်း ဖြေကြားပေးပါ။
Profile ကိုဝင်၍ "My Bookings" Tab တွင် ယခင်သွားခဲ့သော ခရီးစဉ်များနှင့် လက်ရှိ ဘိုကင်များကို ပြန်လည် ကြည့်ရှုနိုင်ပါတယ်။
၉။အသုံးပြုသူမှ  အကြောင်းအမျိုးမျိုးကြောင့် ခရီးစဉ်ကို ရပ်ဆိုင်းလိုက်ရရင် ငွေပြန်အမ်းငွေ (Refund) ကို ဘယ်လောက်ကြာချိန်အတွင်း ရရှိနိုင်လဲ မေးမြန်းလာပါက အောက်ပါအတိုင်း ဖြေကြားပေးပါ:။
ဝန်ဆောင်မှုစည်းကမ်းချက်များနှင့်အညီ ငွေပြန်အမ်းရန် အတည်ပြုပြီးပါက သက်ဆိုင်ရာ ငွေပေးချေမှုစနစ် (KBZPay, Wave Money Account) ထဲသို ၃ ရက်မှ ၅ ရက်အတွင်း အမြန်ဆုံး ပြန်လည်ထည့်သွင်းပေးပါတယ်။
{project_knowledge}
"""

            # OpenAI format အတိုင်း messages များကို စုစည်းခြင်း
            chat_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_latest_message}
            ]

            if not API_KEYS:
                return JsonResponse({'status': 'error', 'message': 'API keys not found in environment variables.'}, status=500)

            response = None
            success = False

            # --- API Key တစ်ခုချင်းစီကို စမ်းသပ်ခေါ်ယူခြင်း ---
            for api_key in API_KEYS:
                try:
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                    )

                    response = client.chat.completions.create(
                        model="google/gemini-2.5-flash", 
                        messages=chat_messages,
                        max_tokens=1000,
                    )
                    
                    success = True
                    break 
                except Exception as key_err:
                    print(f"Key တစ်ခုဖြင့် ချိတ်ဆက်ရာတွင် အမှားရှိ၍ ကျော်သွားသည်: {key_err}")
                    continue 

            if success and response:
                ai_reply = response.choices[0].message.content if response.choices else "ဝမ်းနည်းပါတယ်၊ အဖြေလက်ခံရရှိခြင်း မရှိပါ။"
                return JsonResponse({'status': 'success', 'reply': ai_reply})
            else:
                raise Exception("API Key အားလုံး အလုပ်မလုပ်တော့ပါ သို့မဟုတ် Credits ကုန်နေပါပြီ။")

        except Exception as e:
            traceback.print_exc()
            fallback_reply = "မင်္ဂလာပါ၊ မြန်မာနိုင်ငံ၏ ခရီးသွားနေရာများအကြောင်းကို ကျွန်ုပ် ကူညီဖြေကြားပေးနိုင်ပါသည်။ (ခေတ္တချို့ယွင်းချက်ရှိနေပါသည်)"
            return JsonResponse({'status': 'success', 'reply': fallback_reply})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)