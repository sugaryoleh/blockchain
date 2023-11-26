from django.urls import path

from . import views

urlpatterns = [
    path('profile/', views.profile, name='user-profile'),
    path('update_profile/', views.update_profile, name='update-user-profile'),
    path('replenish/', views.replenish, name='replenish'),
    path('transactions/<str:transaction_type>', views.transactions, name='transactions'),
]
