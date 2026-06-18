import urllib.request
import json

BASE_URL = "http://127.0.0.1:5000/api/measurement"

def stuur(location, height_mm, lat, lon, client_name=None):
    payload = {"location": location, "height_mm": height_mm, "latitude": lat, "longitude": lon}
    if client_name:
        payload["client_name"] = client_name
    data = json.dumps(payload).encode()
    req = urllib.request.Request(BASE_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as r: print(f"  ✓ {location} {height_mm}mm")
    except Exception as e: print(f"  ✗ {e}")

def veld(naam, clat, clon, dlat, dlon, hfn, nx=6, ny=5, client_name=None):
    """Genereert nx×ny meetpunten in een veldrooster met kleine variatie."""
    print(naam)
    for i in range(ny):
        for j in range(nx):
            lat = clat + (i - (ny-1)/2) * dlat / (ny-1)
            lon = clon + (j - (nx-1)/2) * dlon / (nx-1)
            lat += ((i*13+j*7) % 9 - 4) * 0.00004
            lon += ((i*7+j*11) % 9 - 4) * 0.00004
            dy = (lat - clat) / (dlat / 2)
            dx = (lon - clon) / (dlon / 2)
            h = round(max(25, min(350, hfn(dy, dx))), 1)
            stuur(naam, h, lat, lon, client_name=client_name)

# --- Gemeente Groningen velden ---
veld("Sportveld Bedum", 53.3020, 6.5878, 0.0022, 0.0034,
     lambda dy, dx: 55 + dy*22 + dx*6 + dy*dx*5,
     client_name="Gemeente Groningen")

veld("Recreatiegebied Zuidhorn", 53.2469, 6.3925, 0.0022, 0.0036,
     lambda dy, dx: 46 + dy*9 + dx*7 + abs(dy*dx)*6,
     client_name="Gemeente Groningen")

veld("Bedumer bos - Groningen", 53.2930, 6.6002, 0.0022, 0.0036,
     lambda dy, dx: 115 + (1 - dy**2 - dx**2) * 25 + dy*8,
     client_name="Gemeente Groningen")

# --- Interne velden (geen klant) ---
veld("Weiland Usquert", 53.4042, 6.6112, 0.0020, 0.0030,
     lambda dy, dx: 82 + dy*10 + dx*12 + abs(dx)*5)

veld("Polderveld Ten Boer", 53.2682, 6.7037, 0.0020, 0.0032,
     lambda dy, dx: 68 + dx*18 + dy*5 + dx*dx*8)

veld("De Onlanden - Peize", 53.1672, 6.5243, 0.0024, 0.0038,
     lambda dy, dx: 238 + dy*18 - dx*12 + abs(dy - dx)*7)

print("\nKlaar!")
