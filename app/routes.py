from functools import wraps
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import db, limiter
from .models import (
    User,
    ApprovalToken,
    AuditLog,
    RaterApplication,
    Wine,
    NotifyRequest,
    Enquiry,
)
from .services import hash_password, verify_password, send_email, track_event, CELLAR_EMAIL


def approved_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if current_user.status != "APPROVED":
            return redirect(url_for("dashboard"))
        return fn(*args, **kwargs)

    return wrapped


def register_routes(app):
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form["email"].lower().strip()
            if User.query.filter_by(email=email).first():
                flash("Email already registered", "error")
                return redirect(url_for("register"))
            user = User(
                first_name=request.form["first_name"],
                last_name=request.form["last_name"],
                full_address=request.form["full_address"],
                email=email,
                password_hash=hash_password(request.form["password"]),
                marketing_opt_in=bool(request.form.get("marketing_opt_in")),
                status="PENDING",
            )
            db.session.add(user)
            db.session.commit()
            approve_token = ApprovalToken.generate(user.id, "registration", "APPROVE")
            reject_token = ApprovalToken.generate(user.id, "registration", "REJECT")
            base = current_app.config["APPROVAL_BASE_URL"]
            body = f"""
            <h3>New Shornbee registration</h3>
            <p>{user.first_name} {user.last_name} ({user.email})</p>
            <p>Address: {user.full_address}</p>
            <a style='padding:12px 18px;background:#2e7d32;color:white' href='{base}/approval/act?token={approve_token}'>APPROVE</a>
            <a style='padding:12px 18px;background:#b71c1c;color:white' href='{base}/approval/act?token={reject_token}'>REJECT</a>
            """
            send_email("Shornbee registration approval", CELLAR_EMAIL, body)
            flash("Registration received. Pending manual approval to prevent bot/AI-overuse on this free service.", "info")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"].lower().strip()
            user = User.query.filter_by(email=email).first()
            if not user or not verify_password(user.password_hash, request.form["password"]):
                flash("Invalid credentials", "error")
                return redirect(url_for("login"))
            login_user(user)
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("home"))

    @app.route("/approval/act")
    @limiter.limit("20/hour")
    def approval_act():
        token = request.args.get("token", "")
        record, err = ApprovalToken.consume(token)
        if err:
            return f"Approval link {err}.", 400
        user = db.session.get(User, record.user_id)
        if record.purpose == "registration":
            user.status = "APPROVED" if record.action == "APPROVE" else "REJECTED"
        elif record.purpose == "rater":
            appn = RaterApplication.query.filter_by(user_id=user.id, status="PENDING").order_by(RaterApplication.id.desc()).first()
            if appn:
                appn.status = "APPROVED" if record.action == "APPROVE" else "REJECTED"
                if record.action == "APPROVE":
                    user.membership_level = "RATER"
        db.session.add(AuditLog(user_id=user.id, event=f"{record.purpose}_{record.action.lower()}"))
        db.session.commit()
        return "Decision recorded."

    @app.route("/set-locale", methods=["POST"])
    @login_required
    def set_locale():
        locale = request.form.get("locale")
        if locale in ["en-US", "en-GB"]:
            current_user.locale = locale
            db.session.commit()
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        if not current_user.locale:
            return render_template("choose_locale.html")
        if current_user.status == "PENDING":
            return render_template("pending.html")
        if current_user.status == "REJECTED":
            return render_template("rejected.html")
        return render_template("dashboard.html")

    @app.route("/selector")
    @login_required
    @approved_required
    def selector():
        step = int(request.args.get('step', 1))
        if step == 1:
            track_event('wizard_started', current_user.id)
        return render_template('selector.html', step=step)

    @app.route("/selector/confirm", methods=["POST"])
    @login_required
    @approved_required
    def selector_confirm():
        step = int(request.form["step"])
        value = int(request.form["value"])
        session[f"step_{step}"] = value
        track_event("wizard_step_confirmed", current_user.id, {"step": step})
        if step < 3:
            return redirect(url_for('selector', step=step+1))
        hl = session.get("step_1")
        fd = session.get("step_2")
        sb = session.get("step_3")
        weight = "bold" if hl <= 2 else "balanced" if hl == 3 else "light"
        fruit = "fruit-forward" if fd <= 2 else "classic" if fd == 3 else "dry"
        texture = "velvety" if sb <= 2 else "structured" if sb == 3 else "bright"
        if fd == 1:
            persona = f"You enjoy {weight}, fruit-forward reds with a {texture} finish."
        elif fd == 5:
            persona = f"You prefer dry, {weight} reds with a {texture} edge."
        else:
            persona = f"You like {weight} and {texture} reds."
        session["persona"] = persona
        track_event("wizard_completed", current_user.id)
        return redirect(url_for("results"))

    @app.route("/results")
    @login_required
    @approved_required
    def results():
        hl, fd, sb = session.get("step_1"), session.get("step_2"), session.get("step_3")
        if not all([hl, fd, sb]):
            return redirect(url_for("selector"))
        wines = (
            Wine.query.filter_by(
                score_heavy_light=hl,
                score_fruity_dry=fd,
                score_smooth_bright=sb,
            )
            .order_by(Wine.wine_name.asc(), Wine.vintage.asc())
            .all()
        )
        if not wines:
            track_event("zero_match", current_user.id)
        return render_template("results.html", wines=wines, persona=session.get("persona"), hl=hl, fd=fd, sb=sb)

    @app.route("/save-profile", methods=["POST"])
    @login_required
    @approved_required
    def save_profile():
        current_user.last_hl = session.get("step_1")
        current_user.last_fd = session.get("step_2")
        current_user.last_sb = session.get("step_3")
        db.session.commit()
        track_event("profile_saved", current_user.id)
        flash("Saved as My Profile", "success")
        return redirect(url_for("dashboard"))

    @app.route("/use-saved-profile", methods=["POST"])
    @login_required
    @approved_required
    def use_saved_profile():
        if current_user.last_hl and current_user.last_fd and current_user.last_sb:
            session["step_1"] = current_user.last_hl
            session["step_2"] = current_user.last_fd
            session["step_3"] = current_user.last_sb
            session["persona"] = "Using your saved taste profile."
            return redirect(url_for("results"))
        return redirect(url_for("selector"))

    @app.route("/notify-request", methods=["POST"])
    @login_required
    @approved_required
    def notify_request():
        db.session.add(NotifyRequest(user_id=current_user.id, hl=int(request.form["hl"]), fd=int(request.form["fd"]), sb=int(request.form["sb"])))
        db.session.commit()
        flash("Profile saved for future notification.", "info")
        return redirect(url_for("dashboard"))

    @app.route("/rater/apply", methods=["GET", "POST"])
    @login_required
    @approved_required
    def rater_apply():
        if request.method == "POST":
            appn = RaterApplication(
                user_id=current_user.id,
                intended_use=request.form["intended_use"],
                wine_types=request.form["wine_types"],
                expected_frequency=request.form["expected_frequency"],
            )
            db.session.add(appn)
            db.session.commit()
            approve_token = ApprovalToken.generate(current_user.id, "rater", "APPROVE")
            reject_token = ApprovalToken.generate(current_user.id, "rater", "REJECT")
            base = current_app.config["APPROVAL_BASE_URL"]
            body = f"""
            <h3>Rater application</h3>
            <p>User: {current_user.email}</p>
            <p>Use: {appn.intended_use}</p>
            <a style='padding:12px 18px;background:#2e7d32;color:white' href='{base}/approval/act?token={approve_token}'>APPROVE</a>
            <a style='padding:12px 18px;background:#b71c1c;color:white' href='{base}/approval/act?token={reject_token}'>REJECT</a>
            """
            send_email("Shornbee rater approval", CELLAR_EMAIL, body)
            track_event("rater_application_submitted", current_user.id)
            flash("Application submitted.", "success")
            return redirect(url_for("dashboard"))
        return render_template("rater_apply.html")

    @app.route("/my-ratings")
    @login_required
    @approved_required
    def my_ratings():
        return render_template("my_ratings.html")

    @app.route("/contact", methods=["GET", "POST"])
    @login_required
    @limiter.limit("5/hour")
    def contact():
        if request.method == "POST":
            if request.form.get("company"):
                flash("Message blocked.", "error")
                return redirect(url_for("contact"))
            subject = request.form["subject"]
            body = request.form["body"]
            provider_id = send_email(subject, CELLAR_EMAIL, body)
            enquiry = Enquiry(
                user_id=current_user.id,
                from_email=current_user.email,
                subject=subject,
                body=body,
                status="sent",
                provider_id=provider_id,
            )
            db.session.add(enquiry)
            db.session.commit()
            track_event("enquiry_sent", current_user.id)
            flash("Message sent.", "success")
            return redirect(url_for("dashboard"))
        return render_template("contact.html")

    @app.route("/privacy")
    def privacy():
        return render_template("privacy.html")

    @app.route("/terms")
    def terms():
        return render_template("terms.html")
