# Spec: Registration

## Overview
This feature allows new users to create an account on Spendly. It enables the collection of user identity information (name, email) and secure password storage, providing the foundation for authenticated access to personal expense tracking.

## Depends on
- 01-database-setup

## Routes
- `GET /register` — Renders the registration page — public
- `POST /register` — Processes registration form and creates user — public

## Database changes
No database changes. The `users` table created in Step 01 is sufficient.

## Templates
- **Modify:** `templates/register.html` — ensure form fields match the expected POST data (`name`, `email`, `password`) and include basic client-side validation.

## Files to change
- `app.py`: Add the `POST /register` route handler.
- `database/db.py`: Add a helper function `create_user(name, email, password_hash)` to handle the insertion into the `users` table.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] Navigating to `/register` renders the registration form.
- [ ] Submitting the form with valid data creates a new user in the `users` table.
- [ ] User password is stored as a hash, not plain text.
- [ ] Attempting to register with an existing email returns a user-friendly error message.
- [ ] Submitting the form with missing required fields returns a validation error.
- [ ] Successful registration redirects the user to the login page.
