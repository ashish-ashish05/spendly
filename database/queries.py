from datetime import datetime
from database.db import get_db

def get_user_by_id(user_id):
    """
    Fetches a user's profile information.
    Returns a dict with 'name', 'email', 'member_since' or None if not found.
    """
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if user:
            # created_at is in format 'YYYY-MM-DD HH:MM:SS'
            created_at_str = user['created_at']
            dt = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
            member_since = dt.strftime('%B %Y')

            return {
                "name": user['name'],
                "email": user['email'],
                "member_since": member_since
            }
        return None
    finally:
        conn.close()

def get_summary_stats(user_id, start_date=None, end_date=None):
    """
    Calculates spending summary statistics for a user.
    Returns a dict with 'total_spent', 'transaction_count', 'top_category'.
    """
    conn = get_db()
    try:
        # Base query for total spent and transaction count
        query = "SELECT SUM(amount), COUNT(*) FROM expenses WHERE user_id = ?"
        params = [user_id]
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        totals = conn.execute(query, params).fetchone()

        total_spent = totals[0] if totals[0] is not None else 0.0
        transaction_count = totals[1] if totals[1] is not None else 0

        # Top category
        top_cat_query = "SELECT category FROM expenses WHERE user_id = ?"
        top_cat_params = [user_id]
        if start_date:
            top_cat_query += " AND date >= ?"
            top_cat_params.append(start_date)
        if end_date:
            top_cat_query += " AND date <= ?"
            top_cat_params.append(end_date)

        top_cat_query += " GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1"
        top_cat_row = conn.execute(top_cat_query, top_cat_params).fetchone()

        top_category = top_cat_row['category'] if top_cat_row else "—"

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category
        }
    finally:
        conn.close()

def get_recent_transactions(user_id, limit=10, start_date=None, end_date=None):
    """
    Fetches the most recent transactions for a user.
    Returns a list of dicts.
    """
    conn = get_db()
    try:
        query = "SELECT date, description, category, amount FROM expenses WHERE user_id = ?"
        params = [user_id]
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)

        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_category_breakdown(user_id, start_date=None, end_date=None):
    """
    Calculates spending breakdown by category.
    Returns a list of dicts with 'category', 'amount', 'percentage'.
    """
    conn = get_db()
    try:
        query = "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ?"
        params = [user_id]
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " GROUP BY category ORDER BY total DESC"
        rows = conn.execute(query, params).fetchall()

        if not rows:
            return []

        total_spent = sum(row['total'] for row in rows)
        if total_spent == 0:
            return [{"category": row['category'], "amount": row['total'], "percentage": 0} for row in rows]

        breakdown = []
        sum_percentages = 0
        for row in rows:
            percentage = round((row['total'] / total_spent) * 100)
            breakdown.append({
                "category": row['category'],
                "amount": row['total'],
                "percentage": percentage
            })
            sum_percentages += percentage

        # Adjust the largest category to ensure the total is exactly 100%
        diff = 100 - sum_percentages
        if diff != 0:
            breakdown[0]["percentage"] += diff

        return breakdown
    finally:
        conn.close()
