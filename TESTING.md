# Testing Document — Library Management System

## 1. Testing Overview (Repository Reality)

This repository does **not** contain an automated test suite (no `tests.py`, `pytest.ini`, or dedicated test package). Therefore, this document defines an **implementation-aligned manual testing plan** and a test case table that can be executed during evaluation.

Primary test scope is derived from:

- URL routing (`library_project/urls.py`, `accounts/urls.py`, `library/urls.py`)
- Views and business rules (`accounts/views.py`, `library/views.py`)
- Validation (`accounts/forms.py`, `library/forms.py`, `library/models.py`)
- Role checks (`library/decorators.py`)
- Templates and client-side JS (`templates/*`, `static/js/script.js`)

---

## 2. Test Environment

### 2.1 Prerequisites

- Python 3.x (compatible with installed Django version)
- Dependencies installed from `requirements.txt`
  - Django (`>=4.2,<5.0`)
  - Pillow (`>=10.0.0`)

### 2.2 Database setup

- Default database: SQLite (`db.sqlite3`)
- Optional seeding:
  - Command: `python manage.py seed_data`
  - Location: `library/management/commands/seed_data.py`

Seed data provides:

- Admin user: `admin` / `admin123`
- Member user: `john_doe` / `password123`
- Categories and books
- A sample `Borrow` (Pending)

---

## 3. Manual Test Execution Notes

- Many POST operations rely on **CSRF tokens**; tests should be executed via browser (not by pasting POST URLs directly).
- Inventory changes are transactional in:
  - `library.views.approve_borrow`
  - `library.views.return_book`
  - Django Admin action `BorrowAdmin.approve_selected_borrows`

---

## 4. Test Cases Table

Status conventions (recommended for viva/evaluation):

- **Not Run**: testcase prepared but not executed during documentation phase
- **Pass/Fail**: to be filled by evaluator during execution

> Actual Output in this document is intentionally marked as “Not executed” to avoid fabricating results.

| TC ID | Feature | Preconditions | Steps / Input | Expected Output | Actual Output | Status |
|---|---|---|---|---|---|---|
| TC-01 | Home page loads | None | GET `/` | Shows recent books grid and categories | Not executed | Not Run |
| TC-02 | Book list pagination | Seeded books exist | GET `/books/` | Shows list of books; page size 10; pagination controls appear when needed | Not executed | Not Run |
| TC-03 | Book search (title) | Books exist | GET `/books/?query=1984` | Results filtered by title/author `icontains` | Not executed | Not Run |
| TC-04 | Book category filter | Categories exist | GET `/books/?category=<id>` | Only books from the selected category | Not executed | Not Run |
| TC-05 | Book detail shows availability | Book exists | GET `/books/<pk>/` | Shows available copies badge if `available_copies>0` | Not executed | Not Run |
| TC-06 | Register new member | Not logged in | POST `/accounts/register/` (username/email/password1/password2) | User created + added to `Member` group; redirect to login with success message | Not executed | Not Run |
| TC-07 | Register password mismatch blocked | Not logged in | POST register with different password1/password2 | Form errors shown; user not created | Not executed | Not Run |
| TC-08 | Login member redirect | Member exists | POST `/accounts/login/` with member creds | Redirect to `/member/dashboard/` | Not executed | Not Run |
| TC-09 | Login admin redirect | Admin exists | POST `/accounts/login/` with admin creds | Redirect to `/staff-admin/dashboard/` | Not executed | Not Run |
| TC-10 | Logout clears session | Logged in | GET `/accounts/logout/` | Logged out; redirect to home; success message | Not executed | Not Run |
| TC-11 | Borrow request requires login | Not logged in | GET `/borrow/<book_pk>/` | Redirect to login (due to `login_required`) | Not executed | Not Run |
| TC-12 | Borrow request rejects unavailable book | Book has `available_copies=0` | GET/POST borrow | Error message “not available”; redirect to book detail | Not executed | Not Run |
| TC-13 | Borrow request prevents duplicates | Logged in; existing Pending/Approved borrow exists for same book | POST borrow | Error message; no duplicate Borrow created | Not executed | Not Run |
| TC-14 | Borrow request creates Pending borrow | Logged in; book available; no active borrow | POST borrow with future due_date | Borrow created with status Pending; redirect member dashboard | Not executed | Not Run |
| TC-15 | Member dashboard shows active borrows | Member has Pending/Approved borrow(s) | GET `/member/dashboard/` | Active borrows listed; Pending shows “Awaiting approval” | Not executed | Not Run |
| TC-16 | Return blocked for Pending borrow | Member has Pending borrow | GET `/return/<borrow_pk>/` | Error “only return approved”; redirect dashboard | Not executed | Not Run |
| TC-17 | Return blocked for non-owner | Logged in as user A; borrow belongs to user B | GET return URL | Permission error message; redirect dashboard | Not executed | Not Run |
| TC-18 | Approve borrow requires admin | Logged in as Member | GET `/staff-admin/approve/<borrow_pk>/` | Access denied by `admin_required` (redirect to login or blocked) | Not executed | Not Run |
| TC-19 | Admin approves borrow decrements inventory | Admin logged in; book available; borrow Pending | GET approve | Borrow becomes Approved; book `available_copies` decreases by 1 | Not executed | Not Run |
| TC-20 | Admin rejects borrow sets Rejected | Admin logged in; borrow Pending | GET reject | Borrow status becomes Rejected | Not executed | Not Run |
| TC-21 | Return increments inventory | Member owner; borrow Approved | GET return | Borrow becomes Returned with return_date; `available_copies` increases by 1 | Not executed | Not Run |
| TC-22 | Borrow list status filter | Admin logged in | GET `/staff-admin/borrow-requests/?status=Pending` | Only Pending borrows listed | Not executed | Not Run |
| TC-23 | Django admin list pages | Admin logged in | Visit `/admin/` and open Book/Borrow/Category | List/search/filter present as configured in `library/admin.py` | Not executed | Not Run |
| TC-24 | Admin bulk approval action | Pending borrows exist; books available | In Django Admin Borrow list select pending rows → action approve | Selected rows approved; inventory decremented per approval | Not executed | Not Run |

---

## 5. Recommended (Optional) Automated Tests to Add

These are suggestions only; they are not present in the repository. They are included because evaluators often expect a path to automation.

- Unit tests for model validation:
  - `Book.clean()` inventory constraint
  - `Borrow.clean()` due date constraint

- View tests:
  - Borrow request duplicate prevention
  - Approve/return transaction behavior
  - Admin-required access enforcement

- Integration tests:
  - Full borrow lifecycle: Pending → Approved → Returned

---

## 6. Testing Risks / Known Issues Found During Review

- Template issue in `templates/library/users_list.html`:
  - `{{ user.borrows.filter|length }}` is not a valid expression for active borrow counts; the page may not display the intended value.

- Role-based navigation in `templates/base.html`:
  - Uses `user.groups.all.0.name` which assumes group ordering and may misrepresent role links if the user has multiple groups or group order differs.
