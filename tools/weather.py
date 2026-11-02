import os
import requests

# Coordinate dictionary for the 5 store cities
CITY_COORDS = {
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Hyderabad": (17.3850, 78.4867),
    "Bengaluru": (12.9716, 77.5946),
    "Ahmedabad": (23.0225, 72.5714)
}

def get_weather(city: str, date: str) -> dict:
    # 1. Validate City
    if city not in CITY_COORDS:
        return {"ok": False, "error": f"unsupported city: {city}"}
        
    # 2. Validate Date format (YYYY-MM-DD)
    import re
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        return {"ok": False, "error": f"invalid date format: {date}"}
        
    # Check calendar validity
    from datetime import datetime
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"ok": False, "error": f"invalid calendar date: {date}"}

    mode = os.environ.get("WEATHER_MODE", "stub")
    
    if mode == "live":
        # Live mode using Open-Meteo API
        lat, lon = CITY_COORDS[city]
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": date,
            "end_date": date,
            "timezone": "Asia/Kolkata",
            "daily": "temperature_2m_mean,relative_humidity_2m_mean,wind_speed_10m_max,precipitation_sum"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return {"ok": False, "error": f"API returned status code {response.status_code}"}
            
            data = response.json()
            daily = data.get("daily", {})
            
            temp = daily.get("temperature_2m_mean", [0.0])[0]
            humidity = daily.get("relative_humidity_2m_mean", [0.0])[0]
            wind = daily.get("wind_speed_10m_max", [0.0])[0]
            rain = daily.get("precipitation_sum", [0.0])[0]
            
            return {
                "ok": True,
                "city": city,
                "date": date,
                "mode": "live",
                "temperature_c": float(temp) if temp is not None else 0.0,
                "humidity_pct": float(humidity) if humidity is not None else 0.0,
                "wind_kmh": float(wind) if wind is not None else 0.0,
                "rain_mm": float(rain) if rain is not None else 0.0
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
    else:
        # Stub mode (default)
        doy = dt.timetuple().tm_yday
        n = len(city)
        
        temp_c = float(20 + (n + doy) % 15)
        humidity_pct = float(40 + (3 * n + doy) % 50)
        wind_kmh = float(5 + doy % 10)
        rain_mm = 6.5 if doy % 4 == 0 else 0.0
        
        return {
            "ok": True,
            "city": city,
            "date": date,
            "mode": "stub",
            "temperature_c": temp_c,
            "humidity_pct": humidity_pct,
            "wind_kmh": wind_kmh,
            "rain_mm": rain_mm
        }