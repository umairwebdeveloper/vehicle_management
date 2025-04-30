import requests


class MOTAPIError(Exception):
    pass


def fetch_vehicle_from_mot(reg_number: str) -> dict:
    url = f"https://mot.service.gov.uk/trade/vehicles/mot-tests\?registration={reg_number}"
    headers = {
        "x-api-key": "6U4POwrPoW756ESZCC1ic7tTJbTE1Hck5LO6FHTe",
        "Accept": "application/json+v6",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise MOTAPIError("Failed to connect to MOT API") from e
    try:
        return {
            "make": data["make"],
            "model": data["model"],
            "year": int(data["year"]),
            "vin": data.get("vin", ""),
        }
    except (KeyError, ValueError) as e:
        raise MOTAPIError("Invalid data received from MOT API") from e
