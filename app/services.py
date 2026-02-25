import csv
import json
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import AnalyticsEvent, Wine, WineVarietal

CELLAR_EMAIL = "cellarbouncer@mdgloballogistics.com"

I18N = {
    "en-US": {
        "welcome": "Welcome to Shornbee",
        "pending": "Your account is pending Cellar Master approval.",
    },
    "en-GB": {
        "welcome": "Welcome to Shornbee",
        "pending": "Your account is pending Cellar Master approval.",
    },
}


def hash_password(password):
    return generate_password_hash(password)


def verify_password(hashed, password):
    return check_password_hash(hashed, password)


def send_email(subject, to, html_body):
    outbox = Path("tmp")
    outbox.mkdir(exist_ok=True)
    idx = len(list(outbox.glob("mail_*.json"))) + 1
    payload = {"subject": subject, "to": to, "body": html_body}
    (outbox / f"mail_{idx}.json").write_text(json.dumps(payload, indent=2))
    return f"dev-{idx}"


def track_event(name, user_id=None, payload=None):
    event = AnalyticsEvent(user_id=user_id, event_name=name, payload=json.dumps(payload or {}))
    db.session.add(event)
    db.session.commit()


def import_wines_from_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            wine = Wine(
                wine_name=row["wine_name"],
                estate=row["estate"],
                vintage=int(row["vintage"]),
                wine_specific_name=row["wine_specific_name"],
                country=row["country"],
                region=row["region"],
                sub_region=row["sub_region"],
                score_heavy_light=int(row["score_heavy_light"]),
                score_fruity_dry=int(row["score_fruity_dry"]),
                score_smooth_bright=int(row["score_smooth_bright"]),
                winemaker_notes=row["winemaker_notes"],
                md_review=row.get("md_review") or None,
                md_score=float(row["md_score"]) if row.get("md_score") else None,
                lead_varietal=row["lead_varietal"],
            )
            db.session.add(wine)
            db.session.flush()
            for i in range(1, 11):
                varietal_key = f"blend_varietal_{i}"
                pct_key = f"blend_percentage_{i}"
                if row.get(varietal_key):
                    db.session.add(
                        WineVarietal(
                            wine_id=wine.id,
                            varietal=row[varietal_key],
                            percentage=float(row[pct_key]) if row.get(pct_key) else None,
                            sort_order=i,
                        )
                    )
        db.session.commit()
