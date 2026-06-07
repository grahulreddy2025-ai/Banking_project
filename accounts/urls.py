from django.urls import path
from . import views

urlpatterns = [
    path('register/',      views.register_view,      name='register'),
    path('login/',         views.login_view,         name='login'),
    path('dashboard/',     views.dashboard_view,     name='dashboard'),
    path('deposit/',       views.deposit_view,       name='deposit'),
    path('transfer/',      views.transfer_view,      name='transfer'),
    path('transactions/',  views.transactions_view,  name='transactions'),
    path('close-account/', views.close_account_view, name='close_account'),
] 