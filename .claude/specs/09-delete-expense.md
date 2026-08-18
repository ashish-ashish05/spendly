# Spec: Delete Expense

## Overview
Allows users to delete an expense record from their profile. This feature completes the CRUD (Create, Read, Update, Delete) cycle for expense management in Spendly, enabling users to clean up accidental entries or outdated data.

## Depends on
- 07-add-expense
- 08-edit-expense

## Routes
- `GET /expenses/<int:id>/delete` — Deletes a specific expense by ID. Access level: logged-in.

## Database changes
- Create a new helper function `delete_expense(expense_id, user_id)` in `database/queries.py` to perform the deletion.

## Templates
- **Modify:** `templates/profile.html` — Add a "Delete" action link/button for each transaction in the recent transactions list.

## Files to change
- `app.py`
- `database/queries.py`
- `templates/profile.html`

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
- **Ownership Check:** The system must verify that the expense belongs to the currently logged-in user before deleting. If the expense does not exist or belongs to another user, return a 404 error.
- **Destructive Action:** Implement a simple JavaScript `confirm()` dialog on the "Delete" link to prevent accidental deletions.

## Definition of done
- [ ] A "Delete" link is visible for each expense on the profile page.
- [ ] Clicking "Delete" triggers a browser confirmation dialog.
- [ ] If confirmed, the expense is removed from the database.
- [ ] The user is redirected back to the profile page.
- [ ] A success flash message ("Expense deleted successfully!") is displayed.
- [ ] Attempting to delete an expense that doesn't exist or belongs to another user results in a 404 error.
