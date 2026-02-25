import argparse
from app import create_app
from app.services import import_wines_from_csv

parser = argparse.ArgumentParser(description='Import curated wines CSV')
parser.add_argument('csv_path')
args = parser.parse_args()

app = create_app()
with app.app_context():
    import_wines_from_csv(args.csv_path)
    print('Import complete')
