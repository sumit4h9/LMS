from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    description = models.TextField()
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def clean(self):
        # Validation: available_copies must not exceed total_copies
        if self.available_copies > self.total_copies:
            raise ValidationError('Available copies cannot exceed total copies.')
        if self.available_copies < 0:
            raise ValidationError('Available copies cannot be negative.')
        if self.total_copies < 0:
            raise ValidationError('Total copies cannot be negative.')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def is_available(self):
        return self.available_copies > 0
    
    def has_active_borrows(self):
        return self.borrows.filter(status__in=['Pending', 'Approved']).exists()


class Borrow(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Returned', 'Returned'),
        ('Rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrows')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    
    class Meta:
        ordering = ['-borrow_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"
    
    def clean(self):
        # Validation: due_date must be after borrow_date
        if self.due_date and self.borrow_date:
            if self.due_date <= self.borrow_date.date():
                raise ValidationError('Due date must be after borrow date.')
    
    def save(self, *args, **kwargs):
        # Set default due date (14 days from now) if not provided
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        self.full_clean()
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        if self.status == 'Approved' and not self.return_date:
            return timezone.now().date() > self.due_date
        return False
    
    def is_active(self):
        return self.status in ['Pending', 'Approved']
