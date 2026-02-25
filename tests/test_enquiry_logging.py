from app import db
from app.models import Enquiry, User
from app.services import hash_password


def test_enquiry_logged(app, client):
    with app.app_context():
        u = User.query.filter_by(email='ok@example.com').first()
    client.post('/login', data={'email':'ok@example.com','password':'pass'})
    client.post('/contact', data={'subject':'Hi','body':'Help','company':''}, follow_redirects=True)
    with app.app_context():
        e = Enquiry.query.filter_by(from_email='ok@example.com').first()
        assert e is not None
        assert e.status == 'sent'
