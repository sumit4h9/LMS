from django import forms
from .models import Book, Category, Borrow


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'description', 
                  'total_copies', 'available_copies', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or author...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
