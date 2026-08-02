## 1. PostgreSQL Setup

- [x] 1.1 Add `psycopg2-binary` to `requirements.txt` and install
- [x] 1.2 Create database `ykf-interview-project-db`
- [x] 1.3 Create `data/init.sql` DDL script for `users` table (`id SERIAL`, `username VARCHAR UNIQUE`, `password_hash VARCHAR`, `token VARCHAR`)
- [x] 1.4 Create seed data script `data/seed.py` to insert sample users (admin, lawyer01) with bcrypt hashed passwords

## 2. User Data Model & Store

- [x] 2.1 Update `User` dataclass (remove JSON-specific fields, map to PG columns)
- [x] 2.2 Rewrite `auth/store.py`: direct psycopg2 SQL CRUD (find_by_username, update_token, clear_token, find_by_token)
- [x] 2.3 Add `auth/db.py` module: PostgreSQL connection management (connect, get_cursor, close)

## 3. Authentication Service

- [x] 3.1 Retain `hash_password()` and `verify_password()` in `auth/service.py` (no change)
- [x] 3.2 Update `authenticate()` to use PG-backed store (interface unchanged)
- [x] 3.3 Update `login()` to use PG-backed store (interface unchanged)
- [x] 3.4 Update `get_current_user()` to use PG-backed store (interface unchanged)

## 4. Flask API Endpoints

- [x] 4.1 Update `app.py`: add PostgreSQL connection initialization on app startup
- [x] 4.2 Retain `POST /api/login` route (logic stays, underlying store changed)
- [x] 4.3 Add `POST /api/verify` route: parse token, call `get_current_user()`, return JSON
- [x] 4.4 Add `POST /api/logout` route: parse token, clear token in store, return JSON
- [x] 4.5 Remove old JSON file references and cleanup `main.py` if still present

## 5. SPA Shell & Login View

- [x] 5.1 Create `static/index.html` with basic SPA shell (hash routing engine)
- [x] 5.2 Implement `#login` view: username/password form with CSS styling
- [x] 5.3 Implement JS logic: form submit → `fetch POST /api/login` → store token in `localStorage` → navigate to `#home`
- [x] 5.4 Implement route guard: on SPA load, call `/api/verify` with saved token; if valid redirect to `#home`, else show `#login`
- [x] 5.5 Implement logout: `#home` placeholder with logout button, calls `/api/logout`, clears `localStorage`, redirects to `#login`

## 6. Integration Verification

- [x] 6.1 Update `tests/test_auth.py` to use PG test database (or in-memory mock)
- [x] 6.2 Update `tests/test_integration.py` to test `/api/verify` and `/api/logout` endpoints
- [x] 6.3 Manually verify end-to-end flow: browser → SPA load → login → token stored → redirect to #home → logout → back to #login
