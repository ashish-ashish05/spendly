# Spec: Date Filter for Profile Page

## Overview
This feature adds date filtering to the user's profile page. Users can specify a start and end date to filter their spending summary, category breakdown, and transaction list. This allows users to analyze their spending habits over specific time periods (e.g., a specific month or year).

## Depends on
- 04-profile-page
- 05-backend-profile-routes

## Routes
No new routes. The following existing route will be modified:
- `GET /profile` — Now accepts optional `start_date` and `end_date` query parameters to filter displayed data. (Logged-in)

## Database changes
No database changes. Existing queries in `database/queries.py` will be updated to support date range filtering using `WHERE date BETWEEN ? AND ?`.

## Templates
- **Modify:** `templates/profile.html` — Add a date filter form with `start_date` and `end_date` inputs and a "Filter" button.

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
- Date inputs should use `type="date"` in HTML.
- If only one date is provided, it should be treated as a bound (e.g., only `start_date` means from that date onwards).

## Definition of done
- [ ] Date filter form (Start Date, End Date) is visible on the profile page.
- [ ] Applying a date filter updates the "Total Spent" and "Transaction Count" stats.
- [ ] Applying a date filter updates the "Top Category" stat.
- [ ] Applying a date filter updates the "Recent Transactions" list to only show items within the range.
- [ ] Applying a date filter updates the "Category Breakdown" chart/list.
- [ ] Clicking a "Clear Filter" button (or removing dates) restores the view to show all transactions.
- [ ] The app does not crash when invalid date ranges are provided.
