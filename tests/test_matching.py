from app import db
from app.models import Wine

def test_perfect_match_only(app):
    with app.app_context():
        db.session.add(Wine(wine_name='A',estate='E',vintage=2018,wine_specific_name='N',country='X',region='Y',sub_region='Z',score_heavy_light=1,score_fruity_dry=2,score_smooth_bright=3,winemaker_notes='n',lead_varietal='v'))
        db.session.add(Wine(wine_name='B',estate='E',vintage=2017,wine_specific_name='N',country='X',region='Y',sub_region='Z',score_heavy_light=1,score_fruity_dry=2,score_smooth_bright=4,winemaker_notes='n',lead_varietal='v'))
        db.session.commit()
        wines = Wine.query.filter_by(score_heavy_light=1,score_fruity_dry=2,score_smooth_bright=3).all()
        assert len(wines) == 1
        assert wines[0].wine_name == 'A'
