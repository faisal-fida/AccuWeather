# AccuWeather

AccuWeather is a Python-based application designed to provide accurate and real-time weather information. This project leverages the OpenWeatherMap API to fetch and display weather data in a user-friendly format.


## Installation

To get started with AccuWeather, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/faisal-fida/AccuWeather.git
    cd AccuWeather
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up API keys**:
    Create a `.env` file in the root directory (you can copy `.env.example`) and add your API key:
    ```env
    OPENWEATHERMAP_API_KEY=your_actual_api_key_here
    ```

## Usage

Run the application using the following command:
```bash
python app.py
```

AccuWeather will prompt you to enter a city name and will display the current weather details for the specified location.

## Features

- Real-time weather updates using the OpenWeatherMap API.
- Detailed weather information including temperature, humidity, and wind speed.
- User-friendly command-line interface.
- Caching of recent searches to reduce API calls and improve response time.
- Secure API key management using `.env` files.
- Modular code design for better maintainability and testability.
- Comprehensive unit tests for core functionalities.

## Project Structure

```
AccuWeather/
├── app.py                # Main application script
├── requirements.txt      # Project dependencies
├── .env.example          # Example for environment variables file
├── .gitignore            # Specifies intentionally untracked files that Git should ignore
├── README.md             # This file
└── tests/                # Directory for unit tests
    └── test_app.py       # Unit tests for app.py
```

## Complexities

1. **API Integration**: Integrating the OpenWeatherMap API to ensure data accuracy and availability.
2. **Error Handling**: Robust error handling mechanisms to manage API rate limits, network connectivity issues, and invalid user inputs.
3. **Data Parsing**: Efficiently parsing and structuring the API responses for user-friendly display.
4. **Asynchronous Operations (Future)**: Managing asynchronous API calls for improved performance (currently synchronous).

## Solutions

1. **Modular Code Design**: Implemented a modular code structure to isolate different functionalities (API calls, data processing, display), making the codebase easy to maintain, test, and extend.
2. **Caching Mechanism**: Introduced an in-memory, time-based caching mechanism to store frequently accessed data, reducing redundant API calls and improving user experience.
3. **Environment Configuration**: Utilized `.env` files for secure and flexible API key management.
4. **Single API Focus**: Currently focuses on reliable integration with the OpenWeatherMap API. (Designed with future API fallback strategies in mind, should the need arise to incorporate additional data sources).

## Challenges

1. **API Rate Limits**: Managing API rate limits effectively, especially with a free tier API. The caching mechanism helps mitigate this.
2. **Data Consistency**: Ensuring data consistency and accuracy from the OpenWeatherMap API.
3. **User Experience**: Designing a seamless and informative user experience for command-line interactions.
4. **Test Coverage**: Ensuring comprehensive test coverage for all critical components of the application.

[end of README.md]
