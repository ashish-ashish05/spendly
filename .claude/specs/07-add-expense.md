# Spec: Add Expense

## Overview
This feature allows logged-in users to record new expenses. Users can specify the amount, category, date, and an optional description. This is a core functionality of Spendly, moving it from a read-only profile view to an interactive expense tracker.

## Depends on
- 01-database-setup
- 03-login-logout

## Routes
- `GET /expenses/add` — Renders the "Add Expense" form — logged-in
- `POST /expenses/add` — Validates and saves the new expense to the database — logged-in

## Database changes
No database changes. The `expenses` table already exists with the required columns (`user_id`, `amount`, `category`, `date`, `description`).

## Templates
- **Create:** `templates/expenses_add.html` (extends `base.html`)
- **Modify:** `templates/profile.html` (add a "Add Expense" button/link to the add expense page)

## Files to change
- `app.py` (implement the `GET` and `POST` routes for `/expenses/add`)
- `database/queries.py` (add `add_expense(user_id, amount, category, date, description)` helper)
- `templates/profile.html` (add link to the add expense page)

## Files to create
- `templates/expenses_add.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Form validation: ensure `amount`, `category`, and `date` are provided; `amount` must be a positive number.
- Redirect back to `/profile` after successful addition with a success message.

## Definition of done
- [ ] Logged-in user can navigate to `/expenses/add`.
- [ ] Non-logged-in user is redirected to `/login` when accessing `/expenses/add`.
- [ ] "Add Expense" form is rendered correctly with fields for amount, category, date, and description.
- [ ] Submitting the form with missing required fields shows an error message.
- [ ] Submitting the form with a negative amount shows an error message.
- [ ] Successfully adding an expense redirects the user to `/profile` and shows a success flash message.
- [ ] The newly added expense appears in the "Recent Transactions" list on the profile page.
