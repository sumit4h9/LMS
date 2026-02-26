from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    
    # Member pages
    path('member/dashboard/', views.member_dashboard, name='member_dashboard'),
    path('member/borrowed/', views.my_borrowed_books, name='my_borrowed_books'),
    path('member/history/', views.borrow_history, name='borrow_history'),
    path('borrow/<int:pk>/', views.borrow_request, name='borrow_request'),
    path('return/<int:pk>/', views.return_book, name='return_book'),
    
    # Admin pages
    path('staff-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff-admin/borrow-requests/', views.borrow_requests_list, name='borrow_requests_list'),
    path('staff-admin/users/', views.users_list, name='users_list'),
    path('staff-admin/approve/<int:pk>/', views.approve_borrow, name='approve_borrow'),
    path('staff-admin/reject/<int:pk>/', views.reject_borrow, name='reject_borrow'),
]
