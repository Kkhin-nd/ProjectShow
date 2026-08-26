from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

def quick_admin_login(request):
    # database ထဲက admin အကောင့်ကို ရှာပြီး ဝင်ပေးမယ်
    user = User.objects.filter(is_superuser=True).first()
    if user:
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
    return redirect('/admin/')

urlpatterns = [
    # --- Language Switcher URL ---
    path('i18n/', include('django.conf.urls.i18n')), 

    # --- Main Website URLs ---
    path('', views.home, name='home'),
    path('tours/', views.tours_list, name='tours'),
    path('travel-styles/', views.travel_styles, name='travel_styles'),
    path('agents/', views.travel_agents, name='agents'),
    path('seasonal-trips/', views.seasonal_trips, name='seasonal_trips'),
    path('plan-trip/', views.plan_trip_view, name='plan_trip'),
    
    # Package လင့်ခ်အတွက် pk (ID သို့မဟုတ် Slug) ကို အသုံးပြုရန်
    path('package/<str:pk>/', views.package_detail, name='package_detail'),
    
    path('contact/', views.contact_view, name='contact_us'),
    path('about/', views.about_view, name='about'),
    
    # --- Authentication URLs ---
    path('login/', views.login_view, name='login'),      
    path('logout/', views.logout_view, name='logout'),    
    path('register/', views.register_view, name='register'),

    # --- Admin Panel URLs ---
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/packages/', views.admin_packages, name='admin_packages'),
    path('admin-panel/packages/create/', views.create_travel_package_view, name='admin_package_create'),
    path('admin-panel/packages/edit/<int:pk>/', views.admin_package_edit, name='admin_package_edit'),
    path('admin-panel/packages/delete/<int:pk>/', views.admin_package_delete, name='admin_package_delete'),
    
    path('admin-panel/reviews/', views.admin_reviews_view, name='admin_reviews'),
    path('admin-panel/reviews/delete/<int:review_id>/', views.admin_delete_review, name='admin_delete_review'),

    path('admin-panel/agencies/', views.admin_agencies, name='admin_agencies'), 
    path('admin-panel/users/', views.admin_users, name='admin_users'),          
    path('admin-panel/bookings/', views.admin_bookings, name='admin_bookings'), 
    path('admin-panel/agencies/edit/<int:pk>/', views.admin_edit_agency, name='admin_edit_agency'),
    path('admin-panel/agencies/delete/<int:pk>/', views.admin_delete_agency, name='admin_delete_agency'),
    
    # --- Alias URL & User Reviews ---
    path('packages-list/', views.tours_list, name='packages_list'), 
    path('profile/', views.profile_view, name='profile'), 
    path('admin-panel/approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('admin-panel/reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('admin-panel/complete/<int:booking_id>/', views.complete_trip, name='complete_trip'),
    path('user/cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('reviews/', views.reviews_view, name='reviews'), 
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('admin-panel/trip-plans/', views.trip_plan_management_list_view, name='trip_plan_management_list'),
    path('admin-panel/trip-plans/approve/<int:plan_id>/', views.approve_trip_plan, name='approve_trip_plan'),
    path('terms-and-conditions/', views.terms_view, name='terms_condition'),
    
    # --- AI Chat API ---
    path('ai-chat-api/', views.ai_chat_api, name='ai_chat_api'),
    
    path('booking/', views.plan_trip_view, name='booking'),      
]