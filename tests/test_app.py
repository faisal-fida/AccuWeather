import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import time
import io

# Adjust sys.path to allow importing 'app' from the parent directory
# This is necessary for running tests directly if 'app' is not installed as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import the functions and global variables from app.py
# We need to be careful with when app is imported if it has side effects on import
# For this app, it's mostly definitions and loading .env, which is fine for testing.
import app 
from app import (
    process_api_response, 
    call_weather_api, 
    fetch_weather_data, 
    display_weather_info
)
# Import requests exceptions for specific error mocking
from requests.exceptions import Timeout, HTTPError, RequestException, JSONDecodeError


class TestProcessApiResponse(unittest.TestCase):
    def test_valid_data(self):
        mock_json_data = {
            "main": {"temp": 25.5, "humidity": 60},
            "wind": {"speed": 5.5},
            "name": "Test City API"
        }
        expected_output = {
            "temperature": 25.5,
            "humidity": 60,
            "wind_speed": 5.5,
            "city": "Test City API"
        }
        self.assertEqual(process_api_response(mock_json_data, "Test City User"), expected_output)

    def test_missing_keys(self):
        mock_json_data = {"main": {"temp": 25.5}, "name": "Test City"} # Missing humidity, wind
        self.assertIsNone(process_api_response(mock_json_data, "Test City"))

    def test_missing_main_key(self):
        mock_json_data = {"wind": {"speed": 5.5}, "name": "Test City"} # Missing 'main'
        self.assertIsNone(process_api_response(mock_json_data, "Test City"))

    def test_name_fallback(self):
        mock_json_data = {
            "main": {"temp": 25.5, "humidity": 60},
            "wind": {"speed": 5.5} 
            # "name" key missing from API response
        }
        expected_output = {
            "temperature": 25.5,
            "humidity": 60,
            "wind_speed": 5.5,
            "city": "Original City Name" # Should use the fallback
        }
        self.assertEqual(process_api_response(mock_json_data, "Original City Name"), expected_output)


class TestCallWeatherApi(unittest.TestCase):
    @patch('app.requests.get')
    def test_successful_call(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_get.return_value = mock_response

        response = call_weather_api("Test City", "fake_api_key")
        self.assertEqual(response, mock_response)
        mock_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": "Test City", "appid": "fake_api_key", "units": "metric"},
            timeout=10
        )
        response.raise_for_status.assert_called_once()

    @patch('app.requests.get')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_401_error(self, mock_stdout, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 401
        # Configure raise_for_status to simulate HTTPError behavior
        mock_http_error = HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = mock_http_error
        mock_get.return_value = mock_response
        
        self.assertIsNone(call_weather_api("Test City", "fake_api_key"))
        self.assertIn("Error: Invalid API key", mock_stdout.getvalue())

    @patch('app.requests.get')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_404_error(self, mock_stdout, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_http_error = HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = mock_http_error
        mock_get.return_value = mock_response

        self.assertIsNone(call_weather_api("Test City", "fake_api_key"))
        self.assertIn("Error: City 'Test City' not found", mock_stdout.getvalue())

    @patch('app.requests.get')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_timeout_error(self, mock_stdout, mock_get):
        mock_get.side_effect = Timeout
        self.assertIsNone(call_weather_api("Test City", "fake_api_key"))
        self.assertIn("Error: The request to the weather service timed out.", mock_stdout.getvalue())

    @patch('app.requests.get')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_request_exception(self, mock_stdout, mock_get):
        mock_get.side_effect = RequestException("Connection error")
        self.assertIsNone(call_weather_api("Test City", "fake_api_key"))
        self.assertIn("Request error occurred: Connection error", mock_stdout.getvalue())


class TestFetchWeatherData(unittest.TestCase):
    def setUp(self):
        # Reset cache before each test
        app.weather_cache.clear() 

    @patch('app.process_api_response')
    @patch('app.call_weather_api')
    @patch('app.time.time', return_value=1000) # Mock time
    def test_successful_fetch_no_cache(self, mock_time, mock_call_api, mock_process_response):
        mock_api_response = MagicMock() # Mock for requests.Response
        mock_api_response.json.return_value = {"raw_data": "some raw data"}
        mock_call_api.return_value = mock_api_response
        
        processed_data = {"temperature": 10, "city": "Test City Processed"}
        mock_process_response.return_value = processed_data

        result = fetch_weather_data("Test City", "fake_key")

        self.assertEqual(result, processed_data)
        mock_call_api.assert_called_once_with("Test City", "fake_key")
        mock_api_response.json.assert_called_once()
        mock_process_response.assert_called_once_with({"raw_data": "some raw data"}, "Test City")
        
        # Check cache
        self.assertIn("test city", app.weather_cache)
        self.assertEqual(app.weather_cache["test city"]["data"], processed_data)
        self.assertEqual(app.weather_cache["test city"]["timestamp"], 1000)

    @patch('app.call_weather_api')
    @patch('app.time.time', return_value=1000)
    def test_cache_hit(self, mock_time, mock_call_api):
        cached_data = {"temperature": 20, "city": "Cached City"}
        app.weather_cache["cached city"] = {"data": cached_data, "timestamp": 950} # Cache is 50s old

        result = fetch_weather_data("Cached City", "fake_key")
        
        self.assertEqual(result, cached_data)
        mock_call_api.assert_not_called()

    @patch('app.process_api_response')
    @patch('app.call_weather_api')
    @patch('app.time.time') # Mock time for controlling expiry
    def test_cache_expired(self, mock_time, mock_call_api, mock_process_response):
        # Setup: Cache is old
        stale_cached_data = {"temperature": 5, "city": "Stale City"}
        app.weather_cache["stale city"] = {"data": stale_cached_data, "timestamp": 100} # Very old timestamp
        
        # Mock time.time() to return values that make cache stale, then current time for new cache entry
        mock_time.side_effect = [1000, 1000] # First for check, second for new entry (if any)

        # Mock API call and processing for fresh data
        mock_api_response = MagicMock()
        mock_api_response.json.return_value = {"fresh": "data"}
        mock_call_api.return_value = mock_api_response
        
        fresh_data = {"temperature": 25, "city": "Fresh City"}
        mock_process_response.return_value = fresh_data

        result = fetch_weather_data("Stale City", "fake_key")

        self.assertEqual(result, fresh_data)
        mock_call_api.assert_called_once_with("Stale City", "fake_key")
        mock_process_response.assert_called_once_with({"fresh": "data"}, "Stale City")
        self.assertEqual(app.weather_cache["stale city"]["data"], fresh_data)
        self.assertEqual(app.weather_cache["stale city"]["timestamp"], 1000)


    @patch('app.call_weather_api', return_value=None)
    def test_api_call_fails(self, mock_call_api):
        result = fetch_weather_data("Test City", "fake_key")
        self.assertIsNone(result)
        mock_call_api.assert_called_once_with("Test City", "fake_key")
        self.assertNotIn("test city", app.weather_cache) # Ensure nothing was cached

    @patch('app.call_weather_api')
    @patch('sys.stdout', new_callable=io.StringIO) # To capture print output
    def test_json_decoding_fails(self, mock_stdout, mock_call_api):
        mock_response = MagicMock()
        mock_response.json.side_effect = JSONDecodeError("dummy error", "doc", 0)
        mock_call_api.return_value = mock_response
        
        result = fetch_weather_data("Test City", "fake_key")
        
        self.assertIsNone(result)
        mock_call_api.assert_called_once_with("Test City", "fake_key")
        self.assertIn("Error: Could not decode JSON response", mock_stdout.getvalue())
        self.assertNotIn("test city", app.weather_cache)

    @patch('app.process_api_response', return_value=None)
    @patch('app.call_weather_api')
    def test_processing_fails(self, mock_call_api, mock_process_response):
        mock_api_response = MagicMock()
        mock_api_response.json.return_value = {"some": "data"}
        mock_call_api.return_value = mock_api_response
        
        result = fetch_weather_data("Test City", "fake_key")

        self.assertIsNone(result)
        mock_call_api.assert_called_once_with("Test City", "fake_key")
        mock_process_response.assert_called_once_with({"some": "data"}, "Test City")
        self.assertNotIn("test city", app.weather_cache)


class TestDisplayWeatherInfo(unittest.TestCase):
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_display_valid_info(self, mock_stdout):
        weather_info = {
            "temperature": 22.5,
            "humidity": 55,
            "wind_speed": 3.5,
            "city": "Displayed City"
        }
        display_weather_info(weather_info, "User City Input")
        output = mock_stdout.getvalue()
        self.assertIn("Weather in Displayed City:", output)
        self.assertIn("Temperature: 22.5°C", output)
        self.assertIn("Humidity: 55%", output)
        self.assertIn("Wind Speed: 3.5 m/s", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_display_none_info(self, mock_stdout):
        display_weather_info(None, "User City Input")
        output = mock_stdout.getvalue()
        self.assertIn("Failed to retrieve weather information for User City Input.", output)


if __name__ == '__main__':
    unittest.main()
