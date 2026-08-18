# Spec: Edit Expense

## Overview
This feature allows users to modify existing expense records. Users can correct mistakes in the amount, category, date, or description of a transaction. This is a key part of the expense management lifecycle, ensuring the data remains accurate over time.

## Depends on
- 07-add-expense

## Routes
- `GET /expenses/<id>/edit` — Renders the edit form pre-populated with the expense data — logged-in
- `POST /expenses/<id>/edit` — Updates the expense in the database — logged-in

## Database changes
No new tables or columns. New query functions needed in `database/queries.py`:
- `get_expense_by_id(expense_id)`: Fetches a single expense record.
- `update_expense(expense_id, amount, category, date, description)`: Updates an existing record.

## Templates
- **Create:** `templates/expenses_edit.html` (Extends `base.html`)

## Files to change
- `app.py`: Implement `edit_expense` route handlers for GET and POST.
- `database/queries.py`: Implement `get_expense_by_id` and `update_expense`.

## Files to create
- `templates/expenses_edit.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (not applicable here, but standard)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- **Security:** Verify that the expense being edited belongs to the currently logged-in user. If not, return a 403 Forbidden or redirect with an error.

## Definition of done
- [ ] Navigating to `/expenses/<id>/edit` for a valid expense ID shows a form pre-filled with the correct data.
- [ ] Attempting to access the edit page for an expense that doesn't exist returns a 404 error.
- [ ] Attempting to access the edit page for an expense belonging to another user is blocked (e.g., 403 or error message).
- [ ] Submitting the edit form with valid data updates the record in the database.
- [ ] Submitting the edit form with invalid data (e.g., negative amount or empty category) shows a validation error on the page.
- [ ] After a successful update, the user is redirected to the profile page with a success flash message.
