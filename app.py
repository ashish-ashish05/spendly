from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
from database.db import init_db, seed_db, create_user, verify_user

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

    user_profile = {
        "name": "Ashish Kumar",
        "email": "ashish@example.com",
        "member_since": "January 2024"
    }

    summary_stats = {
        "total_spent": "₹45,200",
        "transaction_count": 128,
        "top_category": "Food & Dining"
    }

    recent_transactions = [
        {"date": "Aug 12, 2026", "description": "Starbucks Coffee", "category": "Food", "amount": "₹350"},
        {"date": "Aug 11, 2026", "description": "Uber Trip", "category": "Transport", "amount": "₹420"},
        {"date": "Aug 10, 2026", "description": "Amazon - Keyboard", "category": "Shopping", "amount": "₹2,500"},
        {"date": "Aug 09, 2026", "description": "Grocery Store", "category": "Food", "amount": "₹1,200"},
        {"date": "Aug 08, 2026", "description": "Electric Bill", "category": "Bills", "amount": "₹3,100"},
    ]

    category_breakdown = [
        {"category": "Food", "amount": "₹12,000", "percentage": 26},
        {"category": "Shopping", "amount": "₹15,000", "percentage": 33},
        {"category": "Transport", "amount": "₹8,000", "percentage": 18},
        {"category": "Bills", "amount": "₹10,200", "percentage": 23},
    ]

    return render_template(
        "profile.html",
        user=user_profile,
        stats=summary_stats,
        transactions=recent_transactions,
        categories=category_breakdown
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
