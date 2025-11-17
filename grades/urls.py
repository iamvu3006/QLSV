from django.urls import path
from . import views

urlpatterns = [
    # Subject URLs
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/update/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    # Grade URLs
    path('', views.grade_list, name='grade_list'),
    path('create/', views.grade_create, name='grade_create'),
    path('bulk-create/', views.bulk_grade_create, name='bulk_grade_create'),
    path('<int:pk>/update/', views.grade_update, name='grade_update'),
    path('<int:pk>/delete/', views.grade_delete, name='grade_delete'),
]

