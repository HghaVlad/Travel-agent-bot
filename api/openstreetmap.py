import requests


def get_address(query: str):
    response = requests.get(f"https://nominatim.openstreetmap.org/search.php?q={query}&format=jsonv2").json()
    if len(response) == 0:
        return False

    return sorted(response, key=lambda x: x["importance"])[-1]
