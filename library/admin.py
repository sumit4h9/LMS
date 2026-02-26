from django.contrib import admin
from django.db import transaction
from .models import Category, Book, Borrow


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'available_copies', 'total_copies', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    list_filter = ['category', 'created_at']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'category', 'description', 'cover_image')
        }),
        ('Availability', {
            'fields': ('total_copies', 'available_copies')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def delete_queryset(self, request, queryset):
        """Prevent deletion of books with active borrows"""
        for book in queryset:
            if book.has_active_borrows():
                self.message_user(
                    request,
                    f'Cannot delete "{book.title}" - it has active borrows.',
                    level='ERROR'
                )
            else:
                book.delete()


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'status', 'borrow_date', 'due_date', 'return_date']
    list_filter = ['status', 'borrow_date', 'due_date']
    search_fields = ['user__username', 'book__title']
    readonly_fields = ['borrow_date']
    fieldsets = (
        ('Borrow Information', {
            'fields': ('user', 'book', 'status')
        }),
        ('Dates', {
            'fields': ('borrow_date', 'due_date', 'return_date')
        }),
    )
    
    actions = ['approve_selected_borrows']
    
    def approve_selected_borrows(self, request, queryset):
        """Custom admin action to approve multiple borrow requests"""
        approved_count = 0
        for borrow in queryset:
            if borrow.status == 'Pending' and borrow.book.is_available():
                with transaction.atomic():
                    borrow.status = 'Approved'
                    borrow.save()
                    
                    book = borrow.book
                    book.available_copies -= 1
                    book.save()
                    
                    approved_count += 1
        
        self.message_user(request, f'{approved_count} borrow request(s) approved successfully.')
    
    approve_selected_borrows.short_description = "Approve selected borrow requests"
