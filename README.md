# AccuWeather

AccuWeather is a Python-based application designed to provide accurate and real-time weather information. This project leverages various APIs to fetch and display weather data in a user-friendly format.


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
    Create a `.env` file in the root directory and add your API keys:
    ```env
    WEATHER_API_KEY=your_api_key_here
    ```

## Usage

Run the application using the following command:
```bash
python app.py
```

AccuWeather will prompt you to enter a city name and will display the current weather details for the specified location.

## Features

- Real-time weather updates
- Detailed weather information including temperature, humidity, and wind speed
- User-friendly command-line interface

## Project Structure

```
AccuWeather/
├── app.py
├── README.md
├── requirements.txt
└── .env.example
```

## Complexities

1. **API Integration**: Integrating multiple weather APIs to ensure data accuracy and redundancy.
2. **Error Handling**: Robust error handling mechanisms to manage API rate limits and connectivity issues.
3. **Data Parsing**: Efficiently parsing and structuring the API responses for user-friendly display.

## Solutions

1. **Modular Code Design**: Implemented a modular code structure to isolate different functionalities, making the codebase easy to maintain and extend.
2. **Caching Mechanism**: Introduced a caching mechanism to store frequently accessed data, reducing redundant API calls.
3. **API Fallbacks**: Implemented fallback strategies to switch between APIs in case of failures or rate limit exceedances.

## Challenges

1. **API Rate Limits**: Managing API rate limits was challenging, especially during high usage periods.
2. **Data Consistency**: Ensuring data consistency and accuracy when switching between different APIs.
3. **User Experience**: Designing a seamless user experience for command-line interactions.
