import requests
import folium
import io

OPENROUTESERVICE_API_KEY = "5b3ce3597851110001cf62485c20de94b36640b9b26b675b08d16203"


def get_address(query: str):
    response = requests.get(f"https://nominatim.openstreetmap.org/search.php?q={query}&format=jsonv2").json()
    if len(response) == 0:
        return False

    return sorted(response, key=lambda x: x["importance"])[-1]


def get_distance(location1, location2):
    url = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={OPENROUTESERVICE_API_KEY}&start={location1.lon},{location1.lat}&end={location2.lon},{location2.lat}"
    response = requests.get(url).json()
    return response


def get_route(route_type, location1, location2):
    url = f"https://api.openrouteservice.org/v2/directions/{route_type}?api_key={OPENROUTESERVICE_API_KEY}&start={location1[1]},{location1[0]}&end={location2[1]},{location2[0]}"
    response = requests.get(url).json()
    return response


def create_map(location1, location2, data, zoom):
    my_map = folium.Map(location=location1, zoom_start=zoom)
    folium.Marker(location=location1).add_to(my_map)
    folium.Marker(location=location2).add_to(my_map)
    folium.PolyLine(locations=[list(reversed(coord)) for coord in data['features'][0]['geometry']['coordinates']],
                    color="blue").add_to(my_map)

    return my_map


def route_between_locations(location1, location2, route_type, zoom):
    route = get_route(route_type, location1, location2)
    route_map = create_map(location1, location2, route, zoom)

    img_bytes = io.BytesIO(route_map._to_png())

    return img_bytes, route['features'][0]['properties']['segments'][0]['distance']
