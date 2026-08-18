from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
)
from werkzeug.security import generate_password_hash
from database.db import init_db, seed_db, create_user, verify_user
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown,
    get_expense_by_id,
    update_expense,
    delete_expense,
)

app = Flask(__name__)
app.secret_key = "dev-secret-key-spendly"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        flash("You are already signed in!")
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required")

        password_hash = generate_password_hash(password)
        user_id = create_user(name, email, password_hash)

        if user_id:
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="Email already registered")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        flash("You are already signed in!")
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = verify_user(email, password)
        if user:
            session["user_id"] = user["id"]
            flash("Successfully signed in!")
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #


@app.route("/logout")
def logout():
    if "user_id" not in session:
        return redirect(url_for("login"))

    session.pop("user_id", None)
    flash("Successfully signed out!")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    user_profile = get_user_by_id(user_id)
    summary_stats = get_summary_stats(user_id, start_date, end_date)
    recent_transactions = get_recent_transactions(
        user_id, start_date=start_date, end_date=end_date
    )
    category_breakdown = get_category_breakdown(user_id, start_date, end_date)

    return render_template(
        "profile.html",
        user=user_profile,
        stats=summary_stats,
        transactions=recent_transactions,
        categories=category_breakdown,
        start_date=start_date,
        end_date=end_date,
    )


@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()

        if not amount or not category or not date:
            return render_template(
                "expenses_add.html", error="Amount, category, and date are required"
            )

        try:
            amount_val = float(amount)
            if amount_val <= 0:
                return render_template(
                    "expenses_add.html", error="Amount must be a positive number"
                )
        except ValueError:
            return render_template(
                "expenses_add.html", error="Amount must be a valid number"
            )

        from database.queries import add_expense as db_add_expense

        if db_add_expense(session["user_id"], amount_val, category, date, description):
            flash("Expense added successfully!")
            return redirect(url_for("profile"))
        else:
            return render_template(
                "expenses_add.html", error="Failed to save expense to database"
            )

    return render_template("expenses_add.html")


@app.route("/expenses/<int:id>/edit", methods=["GET", "POST"])
def edit_expense(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    expense = get_expense_by_id(id)

    if not expense or expense["user_id"] != user_id:
        abort(404)

    if request.method == "POST":
        amount = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()

        if not amount or not category or not date:
            return render_template(
                "expenses_edit.html",
                expense=expense,
                error="Amount, category, and date are required",
            )

        try:
            amount_val = float(amount)
            if amount_val <= 0:
                return render_template(
                    "expenses_edit.html",
                    expense=expense,
                    error="Amount must be a positive number",
                )
        except ValueError:
            return render_template(
                "expenses_edit.html",
                expense=expense,
                error="Amount must be a valid number",
            )

        if update_expense(id, amount_val, category, date, description):
            flash("Expense updated successfully!")
            return redirect(url_for("profile"))
        else:
            return render_template(
                "expenses_edit.html",
                expense=expense,
                error="Failed to update expense in database",
            )

    return render_template("expenses_edit.html", expense=expense)


@app.route("/expenses/<int:id>/delete")
def delete_expense_route(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    expense = get_expense_by_id(id)

    if not expense or expense["user_id"] != user_id:
        abort(404)

    if delete_expense(id, user_id):
        flash("Expense deleted successfully!")
        return redirect(url_for("profile"))
    else:
        flash("Failed to delete expense. Please try again.")
        return redirect(url_for("profile"))


# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
