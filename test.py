import urllib.request
import json
import urllib.error

# Dit bestandje is om te gebruiken na het runnen van de app om tests toe te voegen, voel vrij om aan te passen of toe te voegen.

# --------------------------------------------------------

meettechniek = json.dumps({
    "height_mm": 65.2,
    "location": "Schut Geometrische Meettechniek B.V. - Groningen",
    "latitude": 53.2,
    "longitude": 6.6
}).encode("utf-8")

meettechniek_req = urllib.request.Request(
    "http://127.0.0.1:5000/api/measurement",
    data=meettechniek,
    headers={"Content-Type": "application/json"},
    method="POST"
)

# --------------------------------------------------------

hanze = json.dumps({
    "height_mm": 50.0,
    "location": "Hanze-Hogeschool - Groningen",
    "latitude": 53.240635,
    "longitude": 6.533013
}).encode("utf-8")

hanze_req = urllib.request.Request(
    "http://127.0.0.1:5000/api/measurement",
    data=hanze,
    headers={"Content-Type": "application/json"},
    method="POST"
)

# --------------------------------------------------------

spijkerzoon = json.dumps({
    "height_mm": 33.4,
    "location": "Spijkerzoom - Roden",
    "latitude": 53.135343,
    "longitude": 6.437479
}).encode("utf-8")

spijkerzoon_req = urllib.request.Request(
    "http://127.0.0.1:5000/api/measurement",
    data=spijkerzoon,
    headers={"Content-Type": "application/json"},
    method="POST"
)

# --------------------------------------------------------

bedum = json.dumps({
    "height_mm": 80.9,
    "location": "Bedumer bos - Groningen",
    "latitude": 53.292851,
    "longitude": 6.600285
}).encode("utf-8")

bedum_req = urllib.request.Request(
    "http://127.0.0.1:5000/api/measurement",
    data=bedum,
    headers={"Content-Type": "application/json"},
    method="POST"
)

# --------------------------------------------------------

boermapark = json.dumps({
    "height_mm": 70.9,
    "location": "Boermapark - Haren",
    "latitude": 53.292851,
    "longitude": 6.600285
}).encode("utf-8")

boermapark_req = urllib.request.Request(
    "http://127.0.0.1:5000/api/measurement",
    data=boermapark,
    headers={"Content-Type": "application/json"},
    method="POST"
)

# --------------------------------------------------------

onlanden = json.dumps({
    "height_mm": 240.9,
    "location": "De Onlanden - Peize",
    "latitude": 53.166870,
    "longitude": 6.524265
}).encode("utf-8")

onlanden_req = urllib.request.Request(
    "http://127.0.0.1:5000/api/measurement",
    data=onlanden,
    headers={"Content-Type": "application/json"},
    method="POST"
)

# --------------------------------------------------------

try:
    for verzoek in [meettechniek_req, hanze_req, spijkerzoon_req, bedum_req, boermapark_req, onlanden_req]:
        with urllib.request.urlopen(verzoek) as response:
            print(response.read().decode())
except urllib.error.HTTPError as e:
    print("Fout:", e.code, e.read().decode())
except Exception as e:
    print("Fout:", e)