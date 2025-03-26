from django.urls import path
from .views import signup_view, login_view, logout_view, inventory_list, add_item, update_item, delete_item
urlpatterns = [
    path('', inventory_list, name='inventory_list'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('add/', add_item, name='add_item'),
    path('update/<int:pk>/', update_item, name='update_item'),
    path('delete/<int:pk>/', delete_item, name='delete_item'),
]
