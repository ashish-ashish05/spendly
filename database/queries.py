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

def get_summary_stats(user_id):
    """
    Calculates spending summary statistics for a user.
    Returns a dict with 'total_spent', 'transaction_count', 'top_category'.
    """
    conn = get_db()
    try:
        # Total spent and transaction count
        totals = conn.execute(
            "SELECT SUM(amount), COUNT(*) FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        total_spent = totals[0] if totals[0] is not None else 0
        transaction_count = totals[1] if totals[1] is not None else 0

        # Top category
        top_cat_row = conn.execute(
            "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,)
        ).fetchone()

        top_category = top_cat_row['category'] if top_cat_row else "—"

        return {
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "top_category": top_category
        }
    finally:
        conn.close()

def get_recent_transactions(user_id, limit=10):
    """
    Fetches the most recent transactions for a user.
    Returns a list of dicts.
    """
    conn = get_db()
    try:
        cursor = conn.execute(
            "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?",
            (user_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_category_breakdown(user_id):
    """
    Calculates spending breakdown by category.
    Returns a list of dicts with 'category', 'amount', 'percentage'.
    """
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC",
            (user_id,)
        ).fetchall()

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
