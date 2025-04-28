import requests
import datetime
import hashlib
import urllib.parse
import logging
from config import session, weather_cache, CACHE_TIMEOUT, OPENWEATHERMAP_API_KEY, WEATHERAPI_KEY

def get_coordinates(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={urllib.parse.quote(city)},VN&limit=1&appid={OPENWEATHERMAP_API_KEY}"
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:
            return data[0]["lat"], data[0]["lon"], data[0]["name"]
        logging.warning(f"Không tìm thấy tọa độ cho {city}")
        return None, None, None
    except requests.RequestException as e:
        logging.error(f"Lỗi khi gọi Geocoding API: {e}, Response: {response.text if 'response' in locals() else 'N/A'}")
        return None, None, None

def get_weather_forecast(city, date=None):
    cache_key = hashlib.md5(f"{city}_{date}".encode()).hexdigest()
    if cache_key in weather_cache:
        response, timestamp = weather_cache[cache_key]
        if time.time() - timestamp < CACHE_TIMEOUT:
            logging.info(f"Trả về thời tiết từ cache cho {city}")
            return response
    
    try:
        lat, lon, api_city_name = get_coordinates(city)
        if not lat or not lon:
            alternative_names = {
                "Quang Ninh": "Ha Long",
                "Hoi An": "Hội An",
                "Phu Quoc": "Phú Quốc"
            }
            alt_city = alternative_names.get(city, city)
            lat, lon, api_city_name = get_coordinates(alt_city)
            if not lat or not lon:
                return None
        city_display_name = api_city_name if api_city_name else city

        if not date:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=vi"
            response = session.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            result = {
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "city_display_name": city_display_name
            }
            weather_cache[cache_key] = (result, time.time())
            return result

        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=vi"
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        target_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        for daily in data.get("daily", []):
            forecast_date = datetime.datetime.fromtimestamp(daily["dt"]).date()
            if forecast_date == target_date:
                result = {
                    "temp_min": daily["temp"]["min"],
                    "temp_max": daily["temp"]["max"],
                    "description": daily["weather"][0]["description"],
                    "humidity": daily["humidity"],
                    "rain_prob": daily.get("pop", 0) * 100,
                    "city_display_name": city_display_name
                }
                weather_cache[cache_key] = (result, time.time())
                return result
        return None
    except requests.RequestException as e:
        logging.error(f"Lỗi khi lấy thời tiết từ OpenWeatherMap: {e}, Response: {response.text if 'response' in locals() else 'N/A'}")
        return None

def get_weatherapi_forecast(city, date=None):
    cache_key = hashlib.md5(f"{city}_{date}_weatherapi".encode()).hexdigest()
    if cache_key in weather_cache:
        response, timestamp = weather_cache[cache_key]
        if time.time() - timestamp < CACHE_TIMEOUT:
            logging.info(f"Trả về thời tiết từ cache WeatherAPI cho {city}")
            return response
    
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_KEY}&q={urllib.parse.quote(city)}&lang=vi"
        if date:
            url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHERAPI_KEY}&q={urllib.parse.quote(city)}&days=7&lang=vi"
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if not date:
            result = {
                "temp": data["current"]["temp_c"],
                "feels_like": data["current"]["feelslike_c"],
                "humidity": data["current"]["humidity"],
                "description": data["current"]["condition"]["text"],
                "city_display_name": data["location"]["name"]
            }
            weather_cache[cache_key] = (result, time.time())
            return result
        target_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        for forecast in data["forecast"]["forecastday"]:
            forecast_date = datetime.datetime.strptime(forecast["date"], "%Y-%m-%d").date()
            if forecast_date == target_date:
                result = {
                    "temp_min": forecast["day"]["mintemp_c"],
                    "temp_max": forecast["day"]["maxtemp_c"],
                    "description": forecast["day"]["condition"]["text"],
                    "humidity": forecast["day"]["avghumidity"],
                    "rain_prob": forecast["day"]["daily_chance_of_rain"],
                    "city_display_name": data["location"]["name"]
                }
                weather_cache[cache_key] = (result, time.time())
                return result
        return None
    except requests.RequestException as e:
        logging.error(f"Lỗi khi lấy thời tiết từ WeatherAPI: {e}, Response: {response.text if 'response' in locals() else 'N/A'}")
        return None