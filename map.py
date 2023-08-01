import googlemaps
from datetime import datetime
from secret import GM_SECRET_KEY

gmaps = googlemaps.Client(key=GM_SECRET_KEY)

# GEOCODE AN ADDRESS
