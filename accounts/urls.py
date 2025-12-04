from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # ADMIN: Quản lý User
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:pk>/update/', views.admin_user_update, name='admin_user_update'),
    path('admin/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/users/<int:pk>/reset-password/', views.admin_reset_password, name='admin_reset_password'),
    path('admin/users/<int:pk>/toggle-active/', views.admin_toggle_active, name='admin_toggle_active'),
    
    # ADMIN: Quản lý Giáo viên
    path('admin/teachers/', views.admin_teacher_list, name='admin_teacher_list'),
    path('admin/teachers/create/', views.admin_teacher_create, name='admin_teacher_create'),
    path('admin/teachers/<int:pk>/update/', views.admin_teacher_update, name='admin_teacher_update'),
    path('admin/teachers/<int:pk>/delete/', views.admin_teacher_delete, name='admin_teacher_delete'),
]