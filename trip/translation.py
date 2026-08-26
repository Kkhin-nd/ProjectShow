# translation.py
from modeltranslation.translator import translator, TranslationOptions
from .models import TourPackage, Itinerary, TravelAgency

class TourPackageTranslationOptions(TranslationOptions):
    fields = ('title', 'tagline', 'description', 'travel_style', 'price_includes', 'price_excludes', 'duration')

class ItineraryTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

class TravelAgencyTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

translator.register(TourPackage, TourPackageTranslationOptions)
translator.register(Itinerary, ItineraryTranslationOptions)
translator.register(TravelAgency, TravelAgencyTranslationOptions)