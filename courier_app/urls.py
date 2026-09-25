from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('tracking/', views.tracking, name='tracking'),
    path('track/', views.tracking),
    path('track/<str:tracking_number>/', views.tracking_with_number),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('contact/', views.contact, name='contact'),
    path('quote/', views.quote_view, name='quote'),
    path('help/', views.help_center_view, name='help_center'),
    path('api/track/<str:tracking_number>/', views.track_shipment, name='track_shipment'),
    path('api/tracking/<str:tracking_number>/', views.track_shipment),
    path('api/track/<str:tracking_number>/subscribe/', views.api_subscribe_tracking, name='api_subscribe_tracking'),
    path('api/quote/calculate/', views.api_calculate_quote, name='api_calculate_quote'),
]
