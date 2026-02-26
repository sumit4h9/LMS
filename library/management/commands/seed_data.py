from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from library.models import Category, Book, Borrow
from datetime import timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Create groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        member_group, _ = Group.objects.get_or_create(name='Member')
        self.stdout.write('Groups created')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@library.com',
                password='admin123'
            )
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('Admin user created (username: admin, password: admin123)'))
        
        # Create member users
        members_data = [
            ('john_doe', 'john@example.com', 'password123'),
            ('jane_smith', 'jane@example.com', 'password123'),
            ('bob_wilson', 'bob@example.com', 'password123'),
        ]
        
        for username, email, password in members_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.groups.add(member_group)
                self.stdout.write(f'Member user created: {username}')
        
        # Create categories
        categories_data = ['Fiction', 'Science', 'History']
        categories = []
        for cat_name in categories_data:
            category, _ = Category.objects.get_or_create(name=cat_name)
            categories.append(category)
            self.stdout.write(f'Category created: {cat_name}')
        
        # Create books
        books_data = [
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'isbn': '9780061120084',
                'category': categories[0],
                'description': 'A gripping tale of racial injustice and childhood innocence.',
                'total_copies': 5,
                'available_copies': 5,
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'isbn': '9780451524935',
                'category': categories[0],
                'description': 'A dystopian social science fiction novel and cautionary tale.',
                'total_copies': 4,
                'available_copies': 3,
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'isbn': '9780141439518',
                'category': categories[0],
                'description': 'A romantic novel of manners set in Georgian England.',
                'total_copies': 3,
                'available_copies': 3,
            },
            {
                'title': 'A Brief History of Time',
                'author': 'Stephen Hawking',
                'isbn': '9780553380163',
                'category': categories[1],
                'description': 'A landmark volume in science writing.',
                'total_copies': 4,
                'available_copies': 4,
            },
            {
                'title': 'The Selfish Gene',
                'author': 'Richard Dawkins',
                'isbn': '9780198788607',
                'category': categories[1],
                'description': 'A gene-centered view of evolution.',
                'total_copies': 3,
                'available_copies': 2,
            },
            {
                'title': 'Cosmos',
                'author': 'Carl Sagan',
                'isbn': '9780345539434',
                'category': categories[1],
                'description': 'A journey through space and time.',
                'total_copies': 5,
                'available_copies': 5,
            },
            {
                'title': 'Sapiens',
                'author': 'Yuval Noah Harari',
                'isbn': '9780062316097',
                'category': categories[2],
                'description': 'A brief history of humankind.',
                'total_copies': 6,
                'available_copies': 5,
            },
            {
                'title': 'Guns, Germs, and Steel',
                'author': 'Jared Diamond',
                'isbn': '9780393317558',
                'category': categories[2],
                'description': 'The fates of human societies.',
                'total_copies': 3,
                'available_copies': 3,
            },
            {
                'title': 'The Diary of a Young Girl',
                'author': 'Anne Frank',
                'isbn': '9780553577129',
                'category': categories[2],
                'description': 'The poignant diary of a young Jewish girl during WWII.',
                'total_copies': 4,
                'available_copies': 4,
            },
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565',
                'category': categories[0],
                'description': 'A classic American novel of the Jazz Age.',
                'total_copies': 5,
                'available_copies': 4,
            },
        ]
        
        for book_data in books_data:
            if not Book.objects.filter(isbn=book_data['isbn']).exists():
                Book.objects.create(**book_data)
                self.stdout.write(f'Book created: {book_data["title"]}')
        
        # Create sample borrows
        member_user = User.objects.filter(groups__name='Member').first()
        if member_user:
            book = Book.objects.first()
            if book and not Borrow.objects.filter(user=member_user, book=book).exists():
                Borrow.objects.create(
                    user=member_user,
                    book=book,
                    due_date=timezone.now().date() + timedelta(days=14),
                    status='Pending'
                )
                self.stdout.write('Sample borrow created')
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write(self.style.SUCCESS('  Admin - username: admin, password: admin123'))
        self.stdout.write(self.style.SUCCESS('  Member - username: john_doe, password: password123'))
