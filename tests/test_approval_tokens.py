from datetime import datetime, timedelta, timezone
from app import db
from app.models import ApprovalToken, User
from app.services import hash_password


def test_token_single_use_and_hash_only(app):
    with app.app_context():
        u = User(first_name='T',last_name='U',full_address='Addr',email='tok@example.com',password_hash=hash_password('pass'))
        db.session.add(u); db.session.commit()
        raw = ApprovalToken.generate(u.id,'registration','APPROVE')
        rec = ApprovalToken.query.first()
        assert rec.token_hash != raw
        used,_ = ApprovalToken.consume(raw)
        assert used is not None
        _,err = ApprovalToken.consume(raw)
        assert err == 'used'


def test_token_expiry(app):
    with app.app_context():
        u = User(first_name='E',last_name='X',full_address='Addr',email='exp@example.com',password_hash=hash_password('pass'))
        db.session.add(u); db.session.commit()
        raw = ApprovalToken.generate(u.id,'registration','APPROVE')
        rec = ApprovalToken.query.first()
        rec.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db.session.commit()
        _,err = ApprovalToken.consume(raw)
        assert err == 'expired'
