# Library Management System (Django) — Final Year Project Report

Project Title: **Library Management System**  
Platform: **Django (Python) + SQLite**  
Repository: This report is generated strictly from the current repository implementation.

---

## 5. Table of Contents

1. [6. Introduction](#6-introduction)
2. [7. Problem Statement](#7-problem-statement)
3. [8. Existing System](#8-existing-system)
4. [9. Proposed System](#9-proposed-system)
5. [10. Objectives](#10-objectives)
6. [11. Scope of Project](#11-scope-of-project)
7. [12. Functional Requirements](#12-functional-requirements)
8. [13. Non-Functional Requirements](#13-non-functional-requirements)
9. [14. Technology Stack](#14-technology-stack)
10. [15. Software--hardware-requirements](#15-software--hardware-requirements)
11. [16. System Architecture](#16-system-architecture)
12. [17. High Level Design (HLD)](#17-high-level-design-hld)
13. [18. Low Level Design (LLD)](#18-low-level-design-lld)
14. [19. Module Description](#19-module-description)
15. [20. Database Design](#20-database-design)
16. [21. ER Diagram Explanation](#21-er-diagram-explanation)
17. [22. Request-Response Lifecycle](#22-request-response-lifecycle)
18. [23. Authentication & Authorization Flow](#23-authentication--authorization-flow)
19. [24. Security Features](#24-security-features)
20. [25. Transaction Management](#25-transaction-management)
21. [26. API/View Flow](#26-apiview-flow)
22. [27. Django MTV Architecture Explanation](#27-django-mtv-architecture-explanation)
23. [28. Detailed Workflow Explanations](#28-detailed-workflow-explanations)
24. [29. Sequence Flow Descriptions](#29-sequence-flow-descriptions)
25. [30. Form Validation Logic](#30-form-validation-logic)
26. [31. Admin Panel Features](#31-admin-panel-features)
27. [32. Frontend Structure](#32-frontend-structure)
28. [33. File/Folder Structure Explanation](#33-filefolder-structure-explanation)
29. [34. Testing](#34-testing)
30. [35. Test Cases Table](#35-test-cases-table)
31. [36. Advantages](#36-advantages)
32. [37. Limitations](#37-limitations)
33. [38. Future Scope](#38-future-scope)
34. [39. Conclusion](#39-conclusion)
35. [40. References](#40-references)

---

## 6. Introduction

A Library Management System (LMS) helps organize, search, and manage a library’s collection and borrowing operations. This Django-based LMS is implemented as a **server-rendered web application** using Django’s built-in authentication, a small domain model, and role-based workflows.

This implementation supports:

- Public browsing of the catalog
- Member registration/login/logout
- Borrow request creation by members
- Borrow approval/rejection by admins
- Return workflow for approved borrows
- Dashboards for members and admins
- Admin panel management of categories, books, and borrows

The system stores data in SQLite (`db.sqlite3`) and uses Django ORM for persistence.

---

## 7. Problem Statement

Libraries commonly face challenges such as:

- Manual tracking of book inventory (copies available vs total)
- Non-standardized request/approval processes for issuing books
- Lack of real-time visibility into borrow status, due dates, and overdue items
- Difficulty in providing role-based access for staff vs members

The problem is to develop a web-based system that provides a controlled workflow for browsing, borrowing, approvals, and returns, while maintaining data integrity for book availability.

---

## 8. Existing System

In many small or manual library setups, operations rely on:

- Paper registers or spreadsheets for issuance and returns
- Manual counting of copies and availability
- Limited transparency of pending requests and due dates
- No centralized role-based dashboards

These methods are error-prone, do not enforce consistency, and scale poorly.

---

## 9. Proposed System

The proposed system is the implemented Django project in this repository. Its key properties are:

- **Centralized catalog**: `Book` and `Category` models manage catalog data.
- **Borrow lifecycle**: `Borrow` model with status values (`Pending`, `Approved`, `Returned`, `Rejected`).
- **Role separation**:
  - Admin: approves/rejects requests, sees system stats.
  - Member: requests borrows, views active borrows/history, returns books.
- **Consistency via transactions**: inventory updates occur inside `transaction.atomic()`.
- **Search/filter/pagination**: implemented in `book_list` using ORM queries and `Paginator`.

---

## 10. Objectives

Implementation-aligned objectives:

- Provide a public catalog for browsing and viewing book details.
- Enable user registration using Django User model and password validators.
- Implement member borrow request submission with due date.
- Implement admin approval/rejection for borrow requests.
- Maintain book inventory using `available_copies` updates.
- Enable members to return approved borrows and update inventory.
- Provide dashboards that summarize borrowing state and key statistics.

---

## 11. Scope of Project

### In scope (as implemented)

- Server-rendered pages for browsing, borrowing, approving, and returning.
- Group-based roles: Admin and Member.
- SQLite persistence with Django ORM.
- Basic client-side usability JS (confirmation dialogs, required field highlighting, live search filtering on current page).

### Out of scope (not implemented)

- REST API endpoints or mobile app clients
- Fine/penalty calculation for overdue borrows
- Reservation queue / waitlisting
- Notifications (email backend exists for console, but there is no email sending workflow)
- Automated unit/integration tests

---

## 12. Functional Requirements

All functional requirements below map directly to code and templates in the repository.

### 12.1 Public

- View homepage with recent books and categories (`library.views.home` → `templates/library/home.html`).
- Browse all books (`library.views.book_list` → `templates/library/book_list.html`).
- Search books by title or author (`query` GET parameter; `Q(title__icontains) | Q(author__icontains)`).
- Filter books by category (`category` GET parameter). 
- View detailed book information (`library.views.book_detail` → `templates/library/book_detail.html`).

### 12.2 Accounts

- Register a new member (`accounts.views.register_view` + `UserRegistrationForm`).
  - User must provide username, email, and password.
  - Successful registration adds the user to `Member` group.

- Login (`accounts.views.login_view`).
  - Successful login creates a session.
  - Redirect based on role:
    - Admin group or superuser → admin dashboard
    - Otherwise → member dashboard

- Logout (`accounts.views.logout_view`).

### 12.3 Member features (requires login)

- Submit borrow request for a specific book (`library.views.borrow_request`).
  - Must not already have active borrow (Pending/Approved) for that book.
  - Book must be available.
  - Borrow created with status Pending.

- View member dashboard (`library.views.member_dashboard`).
  - Displays active borrows, overdue highlighting, recent history, total borrowed.

- View active borrowed books (`library.views.my_borrowed_books`).
- View full borrow history with pagination (`library.views.borrow_history`).
- Return an approved borrow (`library.views.return_book`).

### 12.4 Admin features (requires login + admin role)

- View admin dashboard statistics (`library.views.admin_dashboard`).
- View borrow requests list with status filter + pagination (`library.views.borrow_requests_list`).
- Approve borrow request (`library.views.approve_borrow`).
  - Transactional update to borrow status and book availability.

- Reject borrow request (`library.views.reject_borrow`).
- View list of registered member users (`library.views.users_list`).
- Use Django Admin panel for CRUD on Category/Book/Borrow (`/admin/`) with custom admin configurations (`library/admin.py`).

---

## 13. Non-Functional Requirements

Derived strictly from the architecture and configuration:

- **Performance**:
  - Search/filter uses indexed-like fields where possible (`isbn` unique); typical SQLite performance for small datasets.
  - Pagination reduces page rendering load for large lists.

- **Security**:
  - CSRF protection via middleware and template tokens.
  - Password validation configured via Django validators.
  - Session-based authentication.

- **Reliability/Data integrity**:
  - Transactions for inventory-related updates.
  - Model-level validation via `full_clean()` on save.

- **Maintainability**:
  - Separation into two apps (`accounts` and `library`).
  - Reusable decorators for role checks.

- **Usability**:
  - Bootstrap UI + client-side confirmations.
  - Messaging framework provides clear feedback.

---

## 14. Technology Stack

### Backend

- Python
- Django (declared in `requirements.txt` as `Django>=4.2,<5.0`)

### Database

- SQLite (`db.sqlite3`), accessed via Django ORM

### Frontend

- Django Templates
- Bootstrap 5.3 via CDN (`templates/base.html`)
- Font Awesome 6.4 via CDN (`templates/base.html`)
- Custom CSS: `static/css/style.css`
- Custom JS: `static/js/script.js`

### Media Handling

- Pillow (`Pillow>=10.0.0`) required for `ImageField` on `Book.cover_image`

---

## 15. Software & Hardware Requirements

### Software

- OS: Windows/macOS/Linux (Django + SQLite are cross-platform)
- Python: 3.x
- Dependencies installed per `requirements.txt`
- Web browser (Chrome/Edge/Firefox)

### Hardware (typical for local evaluation)

- CPU: Dual-core or better
- RAM: 4 GB minimum (8 GB recommended)
- Disk: ~200 MB+ for environment + media + database (depends on uploaded cover images)

---

## 16. System Architecture

The architecture is a monolithic Django application with server-rendered templates.

### 16.1 Architectural layers

- **Presentation**: HTML templates + Bootstrap + custom CSS/JS
- **Application**: URL routing and view functions
- **Domain**: Models (`Category`, `Book`, `Borrow`) and role decorators
- **Data**: SQLite + Django ORM

### 16.2 Component flow (summary)

1. Browser sends GET/POST to Django endpoint.
2. Django routes request to view.
3. View reads/writes domain models using ORM.
4. View renders template or redirects.
5. Messages framework displays feedback in base layout.

---

## 17. High Level Design (HLD)

HLD is captured as major modules and their responsibilities:

- Project config module (`library_project/*`): settings, URLConf, static/media
- Accounts module (`accounts/*`): registration/login/logout
- Library module (`library/*`): catalog, borrowing lifecycle, admin dashboards
- Admin module (`library/admin.py`): admin UI customization and bulk operations
- Presentation module (`templates/*`, `static/*`): UI rendering and browser behavior

See the separate HLD document for diagrams and endpoint mapping: **HLD.md**.

---

## 18. Low Level Design (LLD)

LLD describes the detailed design of:

- Model fields, validations, and helper methods
- View-level preconditions and branching logic
- Transactional update steps
- Template-level role branching and per-page JS

See the separate LLD document with function-by-function mapping and sequences: **LLD.md**.

---

## 19. Module Description

### 19.1 `accounts` module

Key files:

- `accounts/views.py`
  - Implements registration, login, logout
  - Adds registered users to the `Member` group
  - Redirects admins to `/staff-admin/dashboard/`

- `accounts/forms.py`
  - `UserRegistrationForm` extends `UserCreationForm` and includes email

- `templates/accounts/*`
  - `login.html`, `register.html`

### 19.2 `library` module

Key files:

- `library/models.py`
  - `Category`, `Book`, `Borrow`

- `library/views.py`
  - Catalog browsing and book detail
  - Borrow request creation
  - Member dashboard and history
  - Admin dashboards and request management

- `library/decorators.py`
  - `admin_required` used by admin endpoints

- `templates/library/*`
  - `home.html`, `book_list.html`, `book_detail.html`
  - `borrow_request.html`, `member_dashboard.html`, `my_borrowed_books.html`, `borrow_history.html`
  - `admin_dashboard.html`, `borrow_requests_list.html`, `users_list.html`

### 19.3 Management command module

- `library/management/commands/seed_data.py`
  - Seeds groups, users, categories, books, and a sample borrow

---

## 20. Database Design

The database consists of:

- Project domain tables: Category, Book, Borrow
- Django auth tables: User, Group, and their join tables

Key relationships:

- Category 1→N Book
- User 1→N Borrow
- Book 1→N Borrow

See the dedicated database document with schema tables and ER diagram: **DATABASE_DESIGN.md**.

---

## 21. ER Diagram Explanation

The ER model is driven by three domain entities:

- `Category` groups books
- `Book` stores catalog and inventory
- `Borrow` stores borrow requests and their status transitions

Borrow status drives the business workflow:

- Pending: member request waiting for admin decision
- Approved: inventory decremented
- Returned: inventory restored and return_date stored
- Rejected: request refused; inventory unchanged

(Full ER diagram and explanation are in DATABASE_DESIGN.md.)

---

## 22. Request-Response Lifecycle

### 22.1 Example: GET (book list)

1. Browser requests `/books/?query=<q>&category=<id>&page=<n>`.
2. URL routing resolves to `library.views.book_list`.
3. View applies filters using Django ORM (`Q` objects and `filter(category_id=...)`).
4. View paginates results using `Paginator`.
5. View renders `templates/library/book_list.html` with `page_obj`.
6. Browser renders HTML; `static/js/script.js` enables live search filtering on the current page.

### 22.2 Example: POST (borrow request)

1. Member submits borrow form from `/borrow/<pk>/`.
2. `CsrfViewMiddleware` validates CSRF token.
3. View validates availability and duplicate active borrows.
4. View validates `BorrowForm` and saves a `Borrow` row with status Pending.
5. Redirect to member dashboard; success message shown.

---

## 23. Authentication & Authorization Flow

### 23.1 Authentication

- Registration uses `UserRegistrationForm` and creates Django User.
- Login uses `authenticate(request, username, password)` and `login(request, user)`.
- Logout uses `logout(request)`.

Session-based auth is enabled by:

- `SessionMiddleware`
- `AuthenticationMiddleware`

### 23.2 Authorization (Role-Based Access)

- Admin views are protected by `@admin_required` decorator from `library/decorators.py`.
  - Under the hood it uses `user_passes_test(is_admin, login_url='accounts:login')`.

- Member views are protected only by `@login_required` (no `@member_required` is applied).

Navigation role-branching:

- `templates/base.html` shows admin links if `user.is_superuser` OR first group name is Admin.

---

## 24. Security Features

Security features present in code/configuration:

- **CSRF protection**: `CsrfViewMiddleware` enabled; templates include `{% csrf_token %}`.
- **Password validation**: configured in `AUTH_PASSWORD_VALIDATORS`.
- **Session management**: Django sessions are used for logged-in state.
- **Clickjacking mitigation**: `XFrameOptionsMiddleware` enabled.
- **Authorization enforcement**: admin endpoints require admin role via decorator.

Security-related constraints observed:

- `DEBUG=True` and `ALLOWED_HOSTS=[]` indicate development configuration.
- Secret key is hardcoded with placeholder text (development only).

---

## 25. Transaction Management

Transactional integrity is explicitly used where inventory changes occur.

### 25.1 Approve borrow

- Function: `library.views.approve_borrow`
- Transaction block updates:
  - `Borrow.status = 'Approved'`
  - `Book.available_copies -= 1`

### 25.2 Return book

- Function: `library.views.return_book`
- Transaction block updates:
  - `Borrow.status = 'Returned'`
  - `Borrow.return_date = today`
  - `Book.available_copies += 1`

### 25.3 Admin bulk approval

- Function: `BorrowAdmin.approve_selected_borrows` in `library/admin.py`
- Each approved borrow is processed with a transaction.

---

## 26. API/View Flow

This project does not implement REST APIs; the “API” surface is the set of URL endpoints mapped to view functions.

### View flow categories

- Render pages (GET): home, book list, book detail, dashboards, lists
- Create resources (POST): register, login, borrow request
- State transitions (GET triggers): approve, reject, return

Note: Approve/reject/return are triggered by GET requests in this implementation (links/buttons). This is functional but is typically considered less ideal than POST for state changes; it is documented here as implemented.

---

## 27. Django MTV Architecture Explanation

In this project:

- **Model**: `library/models.py` defines business entities (Category, Book, Borrow) and encapsulates validation and domain methods.

- **Template**: HTML templates in `templates/` define presentation:
  - `templates/base.html` defines layout/navigation/messages.
  - `templates/library/*` and `templates/accounts/*` render feature pages.

- **View**: function-based views in `accounts/views.py` and `library/views.py` handle:
  - request parsing
  - authorization checks
  - ORM queries/updates
  - template rendering and redirects

This is a direct implementation of MTV where views orchestrate and models enforce domain invariants.

---

## 28. Detailed Workflow Explanations

### 28.1 Registration flow

- UI: `templates/accounts/register.html`
- Server: `accounts.views.register_view`

Steps:

1. User opens `/accounts/register/`.
2. On submit, server validates form:
   - username, email, password rules via Django validators.
3. Server saves user and adds to `Member` group.
4. Redirect to login with success message.

### 28.2 Login flow

- UI: `templates/accounts/login.html`
- Server: `accounts.views.login_view`

Steps:

1. User submits username/password.
2. Server authenticates.
3. On success, session is created.
4. Role-based redirect:
   - Admin → `/staff-admin/dashboard/`
   - Member → `/member/dashboard/`

### 28.3 Borrow workflow (Member)

- UI: `templates/library/book_detail.html` → Borrow link
- UI form: `templates/library/borrow_request.html`
- Server: `library.views.borrow_request`

Steps:

1. Member clicks Borrow on a book.
2. Server checks:
   - book availability (`Book.is_available()`)
   - existing active borrow request for same book/user
3. Member submits due date.
4. Server creates `Borrow(status='Pending')`.
5. Member dashboard shows “Awaiting approval”.

### 28.4 Approval workflow (Admin)

- UI: `templates/library/admin_dashboard.html` and `borrow_requests_list.html`
- Server: `library.views.approve_borrow` / `reject_borrow`

Approve steps:

1. Admin selects a pending request.
2. Server validates state and availability.
3. In transaction:
   - set status Approved
   - decrement available copies

Reject steps:

1. Admin rejects pending request.
2. Server sets status Rejected.

### 28.5 Return workflow (Member)

- UI: Return link in `templates/library/member_dashboard.html` and `my_borrowed_books.html`
- Server: `library.views.return_book`

Steps:

1. Member clicks Return for an Approved borrow.
2. Server validates ownership and status.
3. In transaction:
   - set status Returned
   - set return_date
   - increment available copies

---

## 29. Sequence Flow Descriptions

Sequence flows for registration, login, borrow, approve, and return are documented in **LLD.md** using mermaid sequence diagrams directly aligned to the view functions.

---

## 30. Form Validation Logic

### 30.1 Server-side

- `accounts/forms.py`:
  - `UserRegistrationForm` inherits Django’s `UserCreationForm` validation.

- `library/models.py`:
  - `Book.save()` enforces `Book.clean()` constraints.
  - `Borrow.save()` enforces `Borrow.clean()` and sets default due date.

- `library/views.py`:
  - Additional business checks (availability, duplicate active borrows, owner checks).

### 30.2 Client-side

- Inline JS validations exist on register/login/borrow pages.
- `static/js/script.js` enhances UX with confirmation dialogs, live search filtering (page-local), and alert dismissal.

---

## 31. Admin Panel Features

Implemented in `library/admin.py`:

- CategoryAdmin
  - list + search by name

- BookAdmin
  - list display includes availability and metadata
  - list filters + search
  - prevents deleting books with active borrows via custom `delete_queryset`

- BorrowAdmin
  - list filters + search
  - custom action: approve selected pending borrows (with availability check and transaction)

Admin site branding is set in `library_project/urls.py`:

- site header/title/index title customized for “Library Management System”

---

## 32. Frontend Structure

Frontend is implemented using:

- `templates/base.html` for layout/navigation/messages
- Bootstrap classes for UI
- Font Awesome icons for visual cues
- `static/css/style.css` for custom styling (hover effects, overdue highlighting, responsive adjustments)
- `static/js/script.js` for UX scripts

Important frontend behaviors:

- Live search filtering on already-rendered book cards via DOM attributes.
- Confirmation prompts for borrow/return and admin actions.
- Auto-dismiss alerts.
- Scroll-to-top button.

---

## 33. File/Folder Structure Explanation

Top-level (repo root) structure:

- `accounts/` — auth views/forms/urls
- `library/` — domain models, views, decorators, admin, migrations, seed command
- `library_project/` — settings and project configuration
- `templates/` — project templates
- `static/` — custom CSS/JS
- `media/` — uploaded cover images
- `db.sqlite3` — SQLite database

The system uses project-level templates (`TEMPLATES['DIRS'] = [BASE_DIR / 'templates']`).

---

## 34. Testing

No automated tests are included in the repository. Manual testing is defined in **TESTING.md**, derived from view logic and templates.

---

## 35. Test Cases Table

A detailed test case table is provided in **TESTING.md** with IDs, preconditions, steps, expected outputs, and placeholders for actual outputs/status.

---

## 36. Advantages

- Simple, clear domain model suitable for academic evaluation.
- Role-based workflows using Django’s standard auth system.
- Inventory consistency protected by transactions.
- Search/filter/pagination implemented using Django ORM.
- Admin panel customized for efficient management.
- Seed script provides repeatable demo dataset.

---

## 37. Limitations

Observed directly from repository:

- No automated unit/integration tests.
- Approve/reject/return operations are triggered via GET requests (links), not POST.
- Template role branching uses `user.groups.all.0.name`, which assumes group ordering.
- `templates/library/users_list.html` contains an invalid attempt at counting active borrows (`user.borrows.filter|length`).
- Version mismatch risk:
  - `requirements.txt` targets Django `<5.0`.
  - Migration file header indicates Django `6.0.2` generated it.

---

## 38. Future Scope

Future improvements that align with the current architecture (not present now):

- Replace state-changing GET links (approve/reject/return) with POST forms.
- Add automated tests for model validation and borrow lifecycle.
- Improve role navigation logic (use `user.groups.filter(name='Admin').exists()` in templates).
- Add proper active borrow count computation for users list.
- Add a fines/penalty subsystem for overdue borrows (would extend `Borrow` model or add a new model).
- Add reservation/hold feature.

---

## 39. Conclusion

This Library Management System is a complete, functional Django application demonstrating:

- Standard Django project structuring with multiple apps
- Use of Django auth and groups for role-based access
- A borrow approval workflow with transactional inventory consistency
- Practical server-rendered UI with search/filter/pagination

The implementation is intentionally simple and academic-friendly, while still showing important engineering concepts such as validation, authorization, and transactional updates.

---

## 40. References

Repository-implemented references:

- Django documentation (conceptual): authentication, messages, ORM, transactions, templates
- Source files in this repository:
  - `library/models.py`, `library/views.py`, `library/admin.py`, `library/decorators.py`
  - `accounts/views.py`, `accounts/forms.py`
  - `library_project/settings.py`, `library_project/urls.py`
  - `templates/*`, `static/*`

Supplementary documents generated with this report:

- `ARCHITECTURE.md`
- `HLD.md`
- `LLD.md`
- `DATABASE_DESIGN.md`
- `TESTING.md`
