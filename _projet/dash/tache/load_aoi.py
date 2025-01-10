from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import Aoi

# populatedplaces_mapping = {
#     'name': 'name',
#     'latitude': 'latitude',
#     'longitude': 'longitude',
#     'pop_max': 'pop_max',
#     'geom': 'POINT',
# }

aoi_mapping = {
    'name': 'name',
    'geom': 'MULTIPOLYGON',
}

aoi_shp = Path(__file__).resolve().parent / 'data' / 'aoi.shp'

def run(verbose=True):
    lm = LayerMapping(Aoi, aoi_shp, aoi_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)



