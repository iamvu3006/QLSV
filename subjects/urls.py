from django.urls import path
from . import views

app_name = 'subjects'

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('create/', views.subject_create, name='subject_create'),
    path('update/<int:pk>/', views.subject_update, name='subject_update'),
    path('delete/<int:pk>/', views.subject_delete, name='subject_delete'),
]