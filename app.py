from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from database import create_tables

app = Flask(__name__)
app.secret_key = "bloodbanksecret"   # needed for flash messages
ADMIN_EMAIL = "ragulraj1625@gmail.com"
create_tables()  # create DB tables when app starts


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- EXTRA UI PAGES ----------------
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/donate")
def donate():
    return render_template("donate.html")


@app.route("/get-involved")
def get_involved():
    return render_template("get_involved.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        conn = sqlite3.connect("bloodbank.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
            (name, email, message)
        )

        conn.commit()
        conn.close()

        flash("Message sent successfully ✅ We will contact you soon!")
        return redirect(url_for("contact"))

    return render_template("contact.html")



# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            conn = sqlite3.connect("bloodbank.db")
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )

            conn.commit()
            conn.close()

            flash("Registration successful! Now login 😄")
            return redirect(url_for("login"))

        except:
            flash("Email already exists! Try another email.")
            return redirect(url_for("register"))

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("bloodbank.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["user_email"] = user[2]
            flash("Login successful 😄")
            return redirect(url_for("dashboard"))
        else:
            flash("Wrong email or password ❌")
            return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first ❌")
        return redirect(url_for("login"))

    return render_template("dashboard.html")

@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session:
        flash("Please login first ❌")
        return redirect(url_for("login"))

    if session.get("user_email") != ADMIN_EMAIL:
        flash("Access denied ❌ Admin only")
        return redirect(url_for("dashboard"))

    conn = sqlite3.connect("bloodbank.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM donors")
    total_donors = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM requests")
    total_requests = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_donors=total_donors,
        total_requests=total_requests,
        total_messages=total_messages
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully 👋")
    return redirect(url_for("login"))


# ---------------- DONOR REGISTER ----------------
@app.route("/donor-register", methods=["GET", "POST"])
def donor_register():
    if "user_id" not in session:
        flash("Please login first ❌")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        blood_group = request.form["blood_group"]
        city = request.form["city"]

        conn = sqlite3.connect("bloodbank.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO donors (name, phone, blood_group, city) VALUES (?, ?, ?, ?)",
            (name, phone, blood_group, city)
        )

        conn.commit()
        conn.close()

        flash("Donor saved successfully 🩸")
        return redirect(url_for("dashboard"))

    return render_template("donor_register.html")


# ---------------- SEARCH DONOR ----------------
@app.route("/search-donor", methods=["GET", "POST"])
def search_donor():
    if "user_id" not in session:
        flash("Please login first ❌")
        return redirect(url_for("login"))

    donors = None

    if request.method == "POST":
        blood_group = request.form["blood_group"]
        city = request.form["city"]

        conn = sqlite3.connect("bloodbank.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM donors WHERE blood_group=? AND city=?",
            (blood_group, city)
        )

        donors = cursor.fetchall()
        conn.close()

    return render_template("search_donor.html", donors=donors)


# ---------------- REQUEST BLOOD ----------------
@app.route("/request-blood", methods=["GET", "POST"])
def request_blood():
    if "user_id" not in session:
        flash("Please login first ❌")
        return redirect(url_for("login"))

    if request.method == "POST":
        patient_name = request.form["patient_name"]
        phone = request.form["phone"]
        blood_group = request.form["blood_group"]
        units = request.form["units"]
        city = request.form["city"]
        reason = request.form["reason"]

        conn = sqlite3.connect("bloodbank.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO requests (patient_name, phone, blood_group, units, city, reason) VALUES (?, ?, ?, ?, ?, ?)",
            (patient_name, phone, blood_group, units, city, reason)
        )

        conn.commit()
        conn.close()

        flash("Blood request submitted successfully 🩸")
        return redirect(url_for("dashboard"))

    return render_template("request_blood.html")


# ---------------- VIEW REQUESTS ----------------
@app.route("/view-requests")
def view_requests():
    if "user_id" not in session:
        flash("Please login first ❌")
        return redirect(url_for("login"))

    # ✅ Admin check
    if session.get("user_email") != ADMIN_EMAIL:
        flash("Access denied ❌ Admin only")
        return redirect(url_for("dashboard"))

    conn = sqlite3.connect("bloodbank.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM requests")
    requests_data = cursor.fetchall()

    conn.close()

    return render_template("view_requests.html", requests=requests_data)


# ---------------- VIEW MESSAGES ----------------
@app.route("/view-messages")
def view_messages():
    if "user_id" not in session:
        flash("Please login first ❌")
        return redirect(url_for("login"))

    # ✅ Admin check
    if session.get("user_email") != ADMIN_EMAIL:
        flash("Access denied ❌ Admin only")
        return redirect(url_for("dashboard"))

    conn = sqlite3.connect("bloodbank.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    messages_data = cursor.fetchall()

    conn.close()

    return render_template("view_messages.html", messages=messages_data)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()

