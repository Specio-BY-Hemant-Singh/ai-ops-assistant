"""
Weather Tool for current weather and forecast information
Uses OpenWeatherMap API
"""
import os
from typing import Dict, Any, Optional
import requests
from .base_tool import BaseTool


class WeatherTool(BaseTool):
    """Tool for getting weather information via OpenWeatherMap API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Weather tool
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            # Use demo mode with limited functionality
            self.api_key = None
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    @property
    def name(self) -> str:
        return "weather"
    
    @property
    def description(self) -> str:
        return "Get current weather information and forecasts for any city"
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "action": "Action to perform: 'current' or 'forecast'",
            "city": "City name (e.g., 'London', 'New York')",
            "country": "Country code (optional, e.g., 'US', 'GB')",
            "units": "Units: 'metric' (Celsius) or 'imperial' (Fahrenheit), default: metric"
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute weather tool action
        
        Args:
            action: 'current' or 'forecast'
            city: City name
            country: Country code (optional)
            units: 'metric' or 'imperial'
            
        Returns:
            Dictionary with weather data
        """
        if not self.api_key:
            return self._demo_weather(**kwargs)
        
        action = kwargs.get("action", "current")
        
        try:
            if action == "current":
                return self._get_current_weather(**kwargs)
            elif action == "forecast":
                return self._get_forecast(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing weather tool: {str(e)}"
            }
    
    def _get_current_weather(self, **kwargs) -> Dict[str, Any]:
        """Get current weather for a city"""
        city = kwargs.get("city")
        country = kwargs.get("country")
        units = kwargs.get("units", "metric")
        
        if not city:
            return {"success": False, "error": "City parameter is required"}
        
        # Build location query
        location = city
        if country:
            location = f"{city},{country}"
        
        # Make API request
        params = {
            "q": location,
            "appid": self.api_key,
            "units": units
        }
        
        response = requests.get(f"{self.base_url}/weather", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Parse response
        temp_unit = "°C" if units == "metric" else "°F"
        
        return {
            "success": True,
            "action": "current",
            "location": {
                "city": data["name"],
                "country": data["sys"]["country"],
                "coordinates": {
                    "latitude": data["coord"]["lat"],
                    "longitude": data["coord"]["lon"]
                }
            },
            "weather": {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "temp_min": data["main"]["temp_min"],
                "temp_max": data["main"]["temp_max"],
                "unit": temp_unit,
                "condition": data["weather"][0]["main"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "clouds": data["clouds"]["all"]
            }
        }
    
    def _get_forecast(self, **kwargs) -> Dict[str, Any]:
        """Get 5-day weather forecast for a city"""
        city = kwargs.get("city")
        country = kwargs.get("country")
        units = kwargs.get("units", "metric")
        
        if not city:
            return {"success": False, "error": "City parameter is required"}
        
        # Build location query
        location = city
        if country:
            location = f"{city},{country}"
        
        # Make API request
        params = {
            "q": location,
            "appid": self.api_key,
            "units": units
        }
        
        response = requests.get(f"{self.base_url}/forecast", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Parse forecast data (3-hour intervals)
        temp_unit = "°C" if units == "metric" else "°F"
        forecasts = []
        
        for item in data["list"][:8]:  # Get next 24 hours (8 * 3-hour intervals)
            forecasts.append({
                "datetime": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "condition": item["weather"][0]["main"],
                "description": item["weather"][0]["description"],
                "humidity": item["main"]["humidity"],
                "wind_speed": item["wind"]["speed"]
            })
        
        return {
            "success": True,
            "action": "forecast",
            "location": {
                "city": data["city"]["name"],
                "country": data["city"]["country"]
            },
            "unit": temp_unit,
            "forecast": forecasts
        }
    
    def _demo_weather(self, **kwargs) -> Dict[str, Any]:
        """
        Return demo weather data when API key is not available
        This allows testing without an API key
        """
        city = kwargs.get("city", "Unknown")
        action = kwargs.get("action", "current")
        units = kwargs.get("units", "metric")
        temp_unit = "°C" if units == "metric" else "°F"
        
        if action == "current":
            return {
                "success": True,
                "action": "current",
                "demo_mode": True,
                "location": {
                    "city": city,
                    "country": "DEMO",
                    "coordinates": {"latitude": 0.0, "longitude": 0.0}
                },
                "weather": {
                    "temperature": 20 if units == "metric" else 68,
                    "feels_like": 18 if units == "metric" else 64,
                    "temp_min": 15 if units == "metric" else 59,
                    "temp_max": 25 if units == "metric" else 77,
                    "unit": temp_unit,
                    "condition": "Clear",
                    "description": "clear sky (demo data)",
                    "humidity": 60,
                    "pressure": 1013,
                    "wind_speed": 3.5,
                    "clouds": 10
                }
            }
        else:
            return {
                "success": True,
                "action": "forecast",
                "demo_mode": True,
                "location": {"city": city, "country": "DEMO"},
                "unit": temp_unit,
                "forecast": [
                    {
                        "datetime": "2024-01-01 12:00:00",
                        "temperature": 20 if units == "metric" else 68,
                        "condition": "Clear",
                        "description": "clear sky (demo)",
                        "humidity": 60,
                        "wind_speed": 3.5
                    }
                ]
            }
