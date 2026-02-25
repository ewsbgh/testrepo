# Shornbee

Mobile-first web app for red wine selection using the Shornbee Consumer Wine Rating System.

## Highlights
- Registration is free and all accounts begin as `PENDING` until Cellar Master approval.
- Secure one-click approval/reject email flow for registration and RATER applications.
- Three-step selector (Heavy-Light, Fruity-Dry, Smooth-Bright) with perfect-match only logic.
- Save profile and reuse on next visit.
- Zero-match profile save for future notifications.
- Contact the Cellar Bouncer form with honeypot + rate limiting + enquiry logging.

## Run locally
```bash
pip install -r requirements.txt
python scripts/apply_migrations.py
python run.py
```

## Import curated wines
```bash
python scripts/import_wines.py scripts/sample_wines.csv
```

## Tests and checks
```bash
python scripts/check_no_snob.py
pytest -q
```
