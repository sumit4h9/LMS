from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Book, Category, Borrow
from .forms import BorrowForm, SearchForm
from .decorators import admin_required, is_admin


def home(request):
    """Public homepage"""
    recent_books = Book.objects.all()[:6]
    categories = Category.objects.all()
    context = {
        'recent_books': recent_books,
        'categories': categories,
    }
    return render(request, 'library/home.html', context)


def book_list(request):
    """Public book list with search and filter"""
    books = Book.objects.all()
    form = SearchForm(request.GET)
    
    # Search by title or author
    query = request.GET.get('query', '')
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(books, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'query': query,
    }
    return render(request, 'library/book_list.html', context)


def book_detail(request, pk):
    """Book detail page"""
    book = get_object_or_404(Book, pk=pk)
    user_has_active_borrow = False
    
    if request.user.is_authenticated:
        user_has_active_borrow = Borrow.objects.filter(
            user=request.user,
            book=book,
            status__in=['Pending', 'Approved']
        ).exists()
    
    context = {
        'book': book,
        'user_has_active_borrow': user_has_active_borrow,
    }
    return render(request, 'library/book_detail.html', context)


@login_required
def borrow_request(request, pk):
    """Member requests to borrow a book"""
    book = get_object_or_404(Book, pk=pk)
    
    # Check if book is available
    if not book.is_available():
        messages.error(request, 'This book is currently not available.')
        return redirect('library:book_detail', pk=pk)
    
    # Check if user already has an active borrow for this book
    existing_borrow = Borrow.objects.filter(
        user=request.user,
        book=book,
        status__in=['Pending', 'Approved']
    ).exists()
    
    if existing_borrow:
        messages.error(request, 'You already have an active borrow request for this book.')
        return redirect('library:book_detail', pk=pk)
    
    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.user = request.user
            borrow.book = book
            borrow.status = 'Pending'
            borrow.save()
            messages.success(request, 'Borrow request submitted successfully!')
            return redirect('library:member_dashboard')
    else:
        # Set default due date to 14 days from now
        initial_due_date = timezone.now().date() + timedelta(days=14)
        form = BorrowForm(initial={'due_date': initial_due_date})
    
    context = {
        'form': form,
        'book': book,
    }
    return render(request, 'library/borrow_request.html', context)


@login_required
def member_dashboard(request):
    """Member dashboard showing borrowed books and history"""
    user = request.user
    
    # Active borrows
    active_borrows = Borrow.objects.filter(
        user=user,
        status__in=['Pending', 'Approved']
    )
    
    # Overdue books
    overdue_books = [b for b in active_borrows if b.is_overdue()]
    
    # Borrow history
    borrow_history = Borrow.objects.filter(user=user).order_by('-borrow_date')[:10]
    
    # Statistics
    total_borrowed = Borrow.objects.filter(user=user).count()
    
    context = {
        'active_borrows': active_borrows,
        'overdue_books': overdue_books,
        'borrow_history': borrow_history,
        'total_borrowed': total_borrowed,
    }
    return render(request, 'library/member_dashboard.html', context)


@login_required
def my_borrowed_books(request):
    """Member's currently borrowed books"""
    active_borrows = Borrow.objects.filter(
        user=request.user,
        status__in=['Pending', 'Approved']
    )
    
    context = {
        'active_borrows': active_borrows,
    }
    return render(request, 'library/my_borrowed_books.html', context)


@login_required
def borrow_history(request):
    """Member's complete borrow history"""
    borrows = Borrow.objects.filter(user=request.user).order_by('-borrow_date')
    
    paginator = Paginator(borrows, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'library/borrow_history.html', context)


@login_required
def return_book(request, pk):
    """Member returns a borrowed book"""
    borrow = get_object_or_404(Borrow, pk=pk)
    
    # Validate ownership
    if borrow.user != request.user:
        messages.error(request, 'You do not have permission to return this book.')
        return redirect('library:member_dashboard')
    
    # Check if already returned
    if borrow.status == 'Returned':
        messages.error(request, 'This book has already been returned.')
        return redirect('library:member_dashboard')
    
    # Check if approved
    if borrow.status != 'Approved':
        messages.error(request, 'You can only return approved borrows.')
        return redirect('library:member_dashboard')
    
    # Return the book using transaction
    with transaction.atomic():
        borrow.status = 'Returned'
        borrow.return_date = timezone.now().date()
        borrow.save()
        
        # Increase available copies
        book = borrow.book
        book.available_copies += 1
        book.save()
    
    messages.success(request, f'You have successfully returned "{book.title}".')
    return redirect('library:member_dashboard')


@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    # Statistics
    total_books = Book.objects.count()
    total_users = User.objects.filter(groups__name='Member').count()
    total_borrowed = Borrow.objects.filter(status='Approved').count()
    pending_requests = Borrow.objects.filter(status='Pending').count()
    
    # Overdue books
    approved_borrows = Borrow.objects.filter(status='Approved')
    overdue_books = [b for b in approved_borrows if b.is_overdue()]
    
    # Recent borrow requests
    recent_requests = Borrow.objects.filter(status='Pending').order_by('-borrow_date')[:5]
    
    context = {
        'total_books': total_books,
        'total_users': total_users,
        'total_borrowed': total_borrowed,
        'pending_requests': pending_requests,
        'overdue_count': len(overdue_books),
        'recent_requests': recent_requests,
    }
    return render(request, 'library/admin_dashboard.html', context)


@login_required
@admin_required
def borrow_requests_list(request):
    """Admin view of all borrow requests"""
    status_filter = request.GET.get('status', '')
    
    if status_filter:
        borrows = Borrow.objects.filter(status=status_filter)
    else:
        borrows = Borrow.objects.all()
    
    borrows = borrows.order_by('-borrow_date')
    
    paginator = Paginator(borrows, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'library/borrow_requests_list.html', context)


@login_required
@admin_required
def approve_borrow(request, pk):
    """Admin approves a borrow request"""
    borrow = get_object_or_404(Borrow, pk=pk)
    
    # Check if already approved
    if borrow.status == 'Approved':
        messages.error(request, 'This borrow request is already approved.')
        return redirect('library:borrow_requests_list')
    
    # Check if rejected
    if borrow.status == 'Rejected':
        messages.error(request, 'Cannot approve a rejected borrow request.')
        return redirect('library:borrow_requests_list')
    
    # Check if book is available
    if not borrow.book.is_available():
        messages.error(request, 'This book is no longer available.')
        return redirect('library:borrow_requests_list')
    
    # Approve using transaction
    with transaction.atomic():
        borrow.status = 'Approved'
        borrow.save()
        
        # Decrease available copies
        book = borrow.book
        book.available_copies -= 1
        book.save()
    
    messages.success(request, f'Borrow request for "{borrow.book.title}" approved.')
    return redirect('library:borrow_requests_list')


@login_required
@admin_required
def reject_borrow(request, pk):
    """Admin rejects a borrow request"""
    borrow = get_object_or_404(Borrow, pk=pk)
    
    if borrow.status != 'Pending':
        messages.error(request, 'Can only reject pending requests.')
        return redirect('library:borrow_requests_list')
    
    borrow.status = 'Rejected'
    borrow.save()
    
    messages.success(request, f'Borrow request for "{borrow.book.title}" rejected.')
    return redirect('library:borrow_requests_list')


@login_required
@admin_required
def users_list(request):
    """Admin view of all users"""
    users = User.objects.filter(groups__name='Member').order_by('-date_joined')
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'library/users_list.html', context)
