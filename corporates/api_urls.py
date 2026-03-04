from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'corporates', api_views.CorporateViewSet, basename='api-corporate')
router.register(r'wallets', api_views.WalletViewSet, basename='api-wallet')
router.register(r'transactions', api_views.TransactionViewSet, basename='api-transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('name-enquiry/', api_views.NameEnquiryView.as_view(), name='api-name-enquiry'),
    
    # Webhook for 9PSB corporate verification
    path('webhooks/corporate-verification/', 
         api_views.CorporateVerificationWebhookView.as_view(), 
         name='api-corporate-verification-webhook'),
    
    # Nested routes for directors
    path('corporates/<uuid:corporate_pk>/directors/', 
         api_views.DirectorViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='api-corporate-directors'),
    path('corporates/<uuid:corporate_pk>/directors/<uuid:pk>/',
         api_views.DirectorViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='api-corporate-director-detail'),
]
