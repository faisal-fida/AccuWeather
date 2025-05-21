# Import necessary modules
import requests
from requests.exceptions import Timeout, HTTPError, RequestException, JSONDecodeError
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Global cache dictionary and cache duration
weather_cache = {}
CACHE_DURATION_SECONDS = 600  # 10 minutes

def call_weather_api(city_name: str, api_key: str) -> requests.Response | None:
    """
    Makes the HTTP GET request to the OpenWeatherMap API.

    Args:
        city_name: The name of the city for the API query.
        api_key: The API key for OpenWeatherMap.

    Returns:
        A requests.Response object if successful, None otherwise.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response
    except HTTPError as http_err:
        # The response object is available here
        if http_err.response.status_code == 401:
            print(f"Error: Invalid API key or API key not authorized. Please check your OPENWEATHERMAP_API_KEY in the .env file.")
        elif http_err.response.status_code == 404:
            print(f"Error: City '{city_name}' not found during API call.")
        else:
            print(f"HTTP error occurred: {http_err} - Status code: {http_err.response.status_code}")
    except Timeout:
        print("Error: The request to the weather service timed out.")
    except RequestException as req_err: # Catches other requests-related errors (e.g., connection error)
        print(f"Request error occurred: {req_err}")
    except Exception as e: # Catch-all for other unexpected errors during API call
        print(f"An unexpected error occurred during API call: {e}")
    return None

def process_api_response(response_json: dict, original_city_name: str) -> dict | None:
    """
    Extracts relevant weather data from the API response JSON.

    Args:
        response_json: The parsed JSON data from the API.
        original_city_name: The city name originally requested by the user.

    Returns:
        A dictionary with weather information if successful, None otherwise.
    """
    try:
        temperature = response_json["main"]["temp"]
        humidity = response_json["main"]["humidity"]
        wind_speed = response_json["wind"]["speed"]
        # Use city name from API response for consistency, fallback to original if not present
        api_city_name = response_json.get("name", original_city_name)

        return {
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "city": api_city_name
        }
    except KeyError as key_err:
        print(f"Error: Could not parse weather data from API response. Missing key: {key_err}")
    except Exception as e: # Catch-all for other unexpected errors during processing
        print(f"An unexpected error occurred while processing API response: {e}")
    return None

def fetch_weather_data(city_name: str, api_key: str) -> dict | None:
    """
    Orchestrates fetching weather data, including caching and API calls.

    Args:
        city_name: The name of the city.
        api_key: The API key for OpenWeatherMap.

    Returns:
        A dictionary containing weather information, or None if an error occurs.
    """
    city_name_normalized = city_name.lower()

    # Check cache first
    if city_name_normalized in weather_cache:
        cached_item = weather_cache[city_name_normalized]
        if time.time() - cached_item["timestamp"] < CACHE_DURATION_SECONDS:
            print(f"Serving from cache for {city_name}")
            return cached_item["data"]
        else:
            print(f"Cache expired for {city_name}")

    print(f"Fetching new data for {city_name}")
    
    response = call_weather_api(city_name, api_key)

    if response:
        try:
            response_json = response.json()
        except JSONDecodeError:
            print("Error: Could not decode JSON response from the weather service.")
            return None
        
        processed_data = process_api_response(response_json, city_name)
        
        if processed_data:
            # Store successful API response in cache
            weather_cache[city_name_normalized] = {
                "data": processed_data,
                "timestamp": time.time()
            }
            return processed_data
    
    # If API call failed or processing failed, response will be None or processed_data will be None
    return None

def display_weather_info(weather_info: dict | None, city_input: str):
    """
    Displays the weather information or an error message.

    Args:
        weather_info: A dictionary with weather data, or None.
        city_input: The city name as entered by the user (for error messages).
    """
    if weather_info:
        print(f"\nWeather in {weather_info['city']}:")
        print(f"  Temperature: {weather_info['temperature']}°C")
        print(f"  Humidity: {weather_info['humidity']}%")
        print(f"  Wind Speed: {weather_info['wind_speed']} m/s")
    else:
        # Specific error messages are printed within the responsible functions.
        # This provides a fallback or summary message.
        print(f"Failed to retrieve weather information for {city_input}.")

# Main part of the script
if __name__ == '__main__':
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")

    if not api_key:
        print("Error: OPENWEATHERMAP_API_KEY not found. Please create a .env file with your API key (e.g., OPENWEATHERMAP_API_KEY=your_key_here).")
        sys.exit(1)

    while True:
        city_input = input("Enter city name (or type 'exit' to quit): ").strip()

        if not city_input:
            print("Error: City name cannot be empty.")
            print("-" * 30)
            continue
        
        if city_input.lower() == 'exit':
            print("Exiting application.")
            break

        weather_information = fetch_weather_data(city_input, api_key)
        display_weather_info(weather_information, city_input)
        print("-" * 30) # Separator for multiple inputs
