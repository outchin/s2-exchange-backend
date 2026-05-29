from django.urls import path

from . import views, auth_views

app_name = 'exchange'

urlpatterns = [
    # Health check
    path('health/', views.health, name='health'),

    # Authentication (Web)
    path('auth/google/', auth_views.google_auth, name='google-auth'),
    path('auth/user/', auth_views.current_user, name='current-user'),
    path('auth/logout/', auth_views.logout_view, name='logout'),

    # Authentication (Mobile - JWT)
    path('auth/google/mobile/', auth_views.google_auth_mobile, name='google-auth-mobile'),
    path('auth/user/mobile/', auth_views.current_user_mobile, name='current-user-mobile'),
    path('auth/logout/mobile/', auth_views.logout_mobile, name='logout-mobile'),
    path('auth/delete-account/mobile/', auth_views.delete_account_mobile, name='delete-account-mobile'),

    # Exchange rates
    path('rates/', views.rate_list, name='rate-list'),
    path('rates/<str:currency_code>/', views.rate_detail, name='rate-detail'),
    path('convert/', views.convert, name='convert'),
    path('rates/<str:currency_code>/sync/', views.sync_rate, name='sync-rate'),

    # Orders
    path('orders/', views.create_order, name='create-order'),
]
