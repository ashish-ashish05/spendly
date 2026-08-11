# Spec: Login and Logout

## Overview
This feature implements the authentication flow for Spendly, allowing registered users to securely log into their accounts and manage their sessions. It ensures that only authenticated users can access personal data (like the profile and expenses pages in future steps).

## Depends on
- 02 registration

## Routes
- `GET /login` — Renders the login page — public
- `POST /login` — Authenticates user and establishes session — public
- `GET /logout` — Terminates the user session and redirects to landing — logged-in

## Database changes
No database schema changes.
Add a helper function `verify_user(email, password)` in `database/db.py` that:
1. Fetches the user by email.
2. Uses `werkzeug.security.check_password_hash` to verify the provided password against the stored hash.
3. Returns the user object (or user ID) if successful, otherwise `None`.

## Templates
- **Modify:** `templates/login.html` — Update to ensure the form uses `POST` and can display error messages passed from the route.

## Files to change
- `app.py` — Implement `POST /login` and `GET /logout` logic; add `secret_key` for session management.
- `database/db.py` — Add `verify_user` helper function.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords verified with `werkzeug.security.check_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `flask.session` to store the `user_id` upon successful login.

## Definition of done
- [ ] User can successfully log in with valid email and password.
- [ ] Login fails with an "Invalid email or password" error for incorrect credentials.
- [ ] Login fails with an "Invalid email or password" error for non-existent emails.
- [ ] User is redirected to the landing page (or profile) upon successful login.
- [ ] User can successfully log out, clearing the session.
- [ ] Attempting to access the `/logout` route while not logged in redirects to the login page.
