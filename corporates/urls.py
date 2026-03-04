from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Corporates
    path('corporates/', views.corporate_list, name='corporate_list'),
    path('corporates/create/', views.corporate_create, name='corporate_create'),
    path('corporates/<uuid:pk>/', views.corporate_detail, name='corporate_detail'),
    path('corporates/<uuid:pk>/edit/', views.corporate_edit, name='corporate_edit'),
    path('corporates/<uuid:pk>/delete/', views.corporate_delete, name='corporate_delete'),
    
    # Directors
    path('corporates/<uuid:corporate_pk>/directors/add/', views.director_add, name='director_add'),
    path('directors/<uuid:pk>/edit/', views.director_edit, name='director_edit'),
    path('directors/<uuid:pk>/delete/', views.director_delete, name='director_delete'),
    
    # Wallets
    path('corporates/<uuid:corporate_pk>/wallet/generate/', views.wallet_generate, name='wallet_generate'),
    path('wallets/', views.wallet_list, name='wallet_list'),
    path('wallets/<uuid:pk>/', views.wallet_detail, name='wallet_detail'),
    path('wallets/<uuid:pk>/refresh/', views.wallet_refresh_balance, name='wallet_refresh_balance'),
    path('wallets/<uuid:pk>/credit/', views.wallet_credit, name='wallet_credit'),
    path('wallets/<uuid:pk>/debit/', views.wallet_debit, name='wallet_debit'),
    path('wallets/<uuid:pk>/transfer/', views.wallet_transfer, name='wallet_transfer'),
    
    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/<uuid:pk>/requery/', views.transaction_requery, name='transaction_requery'),
    
    # Customers (Individual)
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<uuid:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<uuid:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<uuid:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('customers/<uuid:pk>/wallet/generate/', views.customer_wallet_generate, name='customer_wallet_generate'),
    
    # API endpoints
    path('api/name-enquiry/', views.name_enquiry, name='name_enquiry'),
    path('api/verify-bvn/', views.verify_bvn, name='verify_bvn'),
    path('api/verify-nin/', views.verify_nin, name='verify_nin'),
]
