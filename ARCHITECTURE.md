# Library Management System (Django) — Architecture Document

Project type: Django-based Library Management System (monolithic web application)

Repository root: `library_project/` (contains `manage.py`, apps, templates, static assets, and SQLite database)

---

## 1. Architectural Overview

This project is a classic server-rendered Django application using the **MTV (Model–Template–View)** pattern:

- **Models**: Domain entities are defined in `library/models.py`.
- **Views**: Request handling and orchestration live in `accounts/views.py` (auth) and `library/views.py` (library features).
- **Templates**: UI is rendered using Django templates under `templates/` (project-level templates directory configured in `library_project/settings.py`).

It uses Django’s built-in authentication system (`django.contrib.auth`) and role separation via **Groups**:

- `Admin` group: Staff-style features (dashboard, borrow approvals, user list).
- `Member` group: Standard library member features (dashboard, borrow requests, history).

No separate REST API layer exists in this repository; endpoints are standard Django view functions rendering templates and doing redirects.

---

## 2. Runtime Component Diagram (Conceptual)

### Components

- **Browser (Client)**
  - Renders HTML templates
  - Loads Bootstrap and Font Awesome from CDNs (see `templates/base.html`)
  - Executes project JavaScript from `static/js/script.js`

- **Django Application Server**
  - URL routing: `library_project/urls.py`, `accounts/urls.py`, `library/urls.py`
  - View handlers: `accounts/views.py`, `library/views.py`
  - Template engine: configured in `library_project/settings.py`
  - Auth/session middleware: enabled in `MIDDLEWARE`

- **Database (SQLite)**
  - Single file database: `db.sqlite3`
  - Django ORM is used throughout; no raw SQL is present.

- **Static/Media Storage**
  - Static: `static/` (source), `staticfiles/` (collectstatic output directory configured by `STATIC_ROOT`)
  - Media uploads: `media/` with book covers stored under `media/book_covers/` (configured by `MEDIA_ROOT`)

### Mermaid: Component View

```mermaid
flowchart LR
  Browser[Browser
(HTML + Bootstrap + JS)]
  Django[Django Server
URLConf + Views + Templates]
  DB[(SQLite db.sqlite3)]
  Static[(Static Files
/static)]
  Media[(Media Files
/media/book_covers)]

  Browser -->|HTTP GET/POST| Django
  Django -->|ORM| DB
  Browser -->|GET /static/...| Static
  Browser -->|GET /media/...| Media
```

---

## 3. URL Routing Architecture

Top-level routing (`library_project/urls.py`):

- `admin/` → Django Admin
- `accounts/` → Account auth endpoints
- `` (root) → Library app endpoints

Library app routing (`library/urls.py`) separates three categories of pages:

- **Public**
  - `/` → `library.views.home`
  - `/books/` → `library.views.book_list` (search + filter + pagination)
  - `/books/<pk>/` → `library.views.book_detail`

- **Member (requires login)**
  - `/member/dashboard/` → `library.views.member_dashboard`
  - `/member/borrowed/` → `library.views.my_borrowed_books`
  - `/member/history/` → `library.views.borrow_history`
  - `/borrow/<pk>/` → `library.views.borrow_request`
  - `/return/<pk>/` → `library.views.return_book`

- **Staff Admin (requires login + admin group/superuser)**
  - `/staff-admin/dashboard/` → `library.views.admin_dashboard`
  - `/staff-admin/borrow-requests/` → `library.views.borrow_requests_list`
  - `/staff-admin/users/` → `library.views.users_list`
  - `/staff-admin/approve/<pk>/` → `library.views.approve_borrow`
  - `/staff-admin/reject/<pk>/` → `library.views.reject_borrow`

Account routing (`accounts/urls.py`):

- `/accounts/register/` → `accounts.views.register_view`
- `/accounts/login/` → `accounts.views.login_view`
- `/accounts/logout/` → `accounts.views.logout_view`

---

## 4. Middleware & Cross-Cutting Concerns

Middleware is default Django middleware (see `library_project/settings.py`):

- SecurityMiddleware
- SessionMiddleware
- CommonMiddleware
- CsrfViewMiddleware
- AuthenticationMiddleware
- MessageMiddleware
- Clickjacking middleware

Cross-cutting features used by the project:

- **CSRF protection**: enabled globally by middleware and included in POST forms via `{% csrf_token %}` (e.g., `templates/accounts/login.html`, `templates/accounts/register.html`, `templates/library/borrow_request.html`).
- **Session-based auth**: `login()` creates a session; `logout()` clears it.
- **User messaging**: uses Django messages framework (`django.contrib.messages`) for success/error notifications.

---

## 5. Data & Domain Architecture

### Domain Entities (Project-defined)

Defined in `library/models.py`:

- `Category`
  - One-to-many with `Book`

- `Book`
  - FK to `Category`
  - Inventory fields: `total_copies`, `available_copies`
  - `cover_image` stored via Django `ImageField` under `book_covers/`

- `Borrow`
  - FK to `User` (`django.contrib.auth.models.User`)
  - FK to `Book`
  - State machine-ish `status`: Pending → Approved → Returned (or Pending → Rejected)

### Roles (Auth)

No custom user model exists (`accounts/models.py` states it uses Django User/Group).

Groups are created/ensured by management command `library/management/commands/seed_data.py`:

- `Admin`
- `Member`

Role checks:

- `library/decorators.py` provides `is_admin`, `is_member`, `admin_required`, `member_required`.
- Admin-only views are decorated with `@admin_required`.

---

## 6. Transaction & Consistency Design

This project uses **transaction boundaries** for inventory-related state changes using `django.db.transaction.atomic()`:

- `library.views.approve_borrow(pk)`
  - Sets `Borrow.status='Approved'`
  - Decrements `Book.available_copies` by 1

- `library.views.return_book(pk)`
  - Sets `Borrow.status='Returned'` and `Borrow.return_date`
  - Increments `Book.available_copies` by 1

- Django Admin action `BorrowAdmin.approve_selected_borrows()` in `library/admin.py`
  - Batch-approves pending borrows (when book is available)
  - Decrements book availability inside a transaction

These operations are implemented as **read–validate–write** sequences and rely on database transactions to keep borrow state and inventory in sync.

---

## 7. Error Handling & UX Patterns

Patterns used:

- Redirects with user messages (`messages.success`, `messages.error`) after state-changing operations.
- Defensive checks before writes:
  - Book availability via `Book.is_available()`
  - Duplicate/active borrow prevention via ORM existence checks
  - Ownership validation on return

Templates provide user feedback through Bootstrap alerts in `templates/base.html`.

Note: `templates/403.html` and `templates/404.html` exist, but this repository does not define `handler403`/`handler404` in URLConf; whether they are used depends on Django’s template resolution and server configuration.

---

## 8. Deployment View

This repository includes both WSGI and ASGI entry points:

- `library_project/wsgi.py` for traditional WSGI servers
- `library_project/asgi.py` for ASGI servers

The project is configured for local/development execution (SQLite, `DEBUG=True`, console email backend).

---

## 9. Key Architectural Constraints & Observations (Implementation-Aligned)

- **Monolith**: no service separation; all features share a single Django project.
- **No REST API**: all access is through server-rendered pages.
- **Simple domain**: only three project models.
- **Role enforcement**: enforced in Python views via decorators; navigation also branches in templates (see `templates/base.html`).
- **Version inconsistency**: `requirements.txt` constrains Django to `>=4.2,<5.0`, while `library/migrations/0001_initial.py` indicates it was generated by Django `6.0.2` (timestamp 2026-02-24). This should be reconciled for consistent environments.
