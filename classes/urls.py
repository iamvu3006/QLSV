from django.urls import path
from . import views

urlpatterns = [
    path('', views.class_list, name='class_list'),
    path('<int:pk>/', views.class_detail, name='class_detail'),
    path('create/', views.class_create, name='class_create'),
    path('<int:pk>/update/', views.class_update, name='class_update'),
    path('<int:pk>/delete/', views.class_delete, name='class_delete'),
    path('<int:pk>/add-student/', views.class_add_student, name='class_add_student'),
    path('<int:pk>/remove-student/<int:student_id>/', views.class_remove_student, name='class_remove_student'),
]

