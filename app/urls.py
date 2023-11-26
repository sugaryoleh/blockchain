from django.urls import path

from . import views

urlpatterns = [
    path('profile/', views.profile, name='user-profile'),
    path('update_profile/', views.update_profile, name='update-user-profile'),
    path('create_transaction/', views.create_transaction, name='create-transaction'),
    path('replenish/', views.replenish, name='replenish'),
    path('transaction_list/<str:transaction_type>', views.transactions, name='transaction-list'),
]
