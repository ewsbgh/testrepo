from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from flask_login import UserMixin
from . import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    full_address = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    marketing_opt_in = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="PENDING")
    membership_level = db.Column(db.String(20), default="BASIC")
    locale = db.Column(db.String(10), nullable=True)
    last_hl = db.Column(db.Integer, nullable=True)
    last_fd = db.Column(db.Integer, nullable=True)
    last_sb = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class ApprovalToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # registration / rater
    action = db.Column(db.String(10), nullable=False)  # APPROVE / REJECT
    token_hash = db.Column(db.String(64), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def generate(user_id, purpose, action):
        raw = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw.encode()).hexdigest()
        record = ApprovalToken(
            user_id=user_id,
            purpose=purpose,
            action=action,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.session.add(record)
        db.session.commit()
        return raw

    @staticmethod
    def consume(raw_token):
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        record = ApprovalToken.query.filter_by(token_hash=token_hash).first()
        if not record:
            return None, "invalid"
        now = datetime.now(timezone.utc)
        expires = record.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if record.used_at:
            return None, "used"
        if expires < now:
            return None, "expired"
        record.used_at = now
        db.session.commit()
        return record, None


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event = db.Column(db.String(80), nullable=False)
    meta = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class RaterApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    intended_use = db.Column(db.Text, nullable=False)
    wine_types = db.Column(db.Text, nullable=False)
    expected_frequency = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default="PENDING")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Wine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wine_name = db.Column(db.String(255), nullable=False)
    estate = db.Column(db.String(255), nullable=False)
    vintage = db.Column(db.Integer, nullable=False)
    wine_specific_name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    region = db.Column(db.String(120), nullable=False)
    sub_region = db.Column(db.String(120), nullable=False)
    score_heavy_light = db.Column(db.Integer, nullable=False)
    score_fruity_dry = db.Column(db.Integer, nullable=False)
    score_smooth_bright = db.Column(db.Integer, nullable=False)
    winemaker_notes = db.Column(db.Text, nullable=False)
    md_review = db.Column(db.Text, nullable=True)
    md_score = db.Column(db.Float, nullable=True)
    lead_varietal = db.Column(db.String(120), nullable=False)

    __table_args__ = (
        db.Index(
            "idx_wine_scores",
            "score_heavy_light",
            "score_fruity_dry",
            "score_smooth_bright",
        ),
    )


class WineVarietal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wine_id = db.Column(db.Integer, db.ForeignKey("wine.id"), nullable=False)
    varietal = db.Column(db.String(120), nullable=False)
    percentage = db.Column(db.Float, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=1)


class NotifyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    hl = db.Column(db.Integer, nullable=False)
    fd = db.Column(db.Integer, nullable=False)
    sb = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Enquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    from_email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False)
    provider_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class AnalyticsEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    event_name = db.Column(db.String(80), nullable=False)
    payload = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
