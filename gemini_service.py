import google.generativeai as genai
from config import GEMINI_API_KEY
import json

class GeminiService:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_itinerary_summary(self, city, budget, days):
        prompt = f"""
        Create a travel itinerary summary for {city} with a budget of ${budget} for {days} days.
        Return only a JSON object with this structure:
        {{
            "city": "{city}",
            "total_budget": {budget},
            "duration": {days},
            "overview": "brief overview of the trip",
            "budget_breakdown": {{
                "accommodation": "amount",
                "food": "amount", 
                "activities": "amount",
                "transport": "amount"
            }},
            "best_time_to_visit": "season/months",
            "currency": "local currency"
        }}
        """
        
        response = self.model.generate_content(prompt)
        return self._parse_json_response(response.text)
    
    def generate_daily_itinerary(self, city, day_number, budget_per_day):
        prompt = f"""
        Create a detailed day {day_number} itinerary for {city} with a daily budget of ${budget_per_day}.
        Return only a JSON object with this structure:
        {{
            "day": {day_number},
            "theme": "day theme (e.g., Historical Sites, Cultural Experience)",
            "activities": [
                {{
                    "time": "9:00 AM",
                    "activity": "activity name",
                    "location": "specific location",
                    "duration": "2 hours",
                    "cost": "estimated cost",
                    "description": "brief description"
                }}
            ],
            "transportation": "how to get around",
            "daily_budget_used": "total estimated cost"
        }}
        Include 4-6 activities per day covering morning, afternoon, and evening.
        """
        
        response = self.model.generate_content(prompt)
        return self._parse_json_response(response.text)
    
    def generate_dining_recommendations(self, city, budget_range):
        prompt = f"""
        Generate dining recommendations for {city} within {budget_range} budget range.
        Return only a JSON object with this structure:
        {{
            "dining_recommendations": [
                {{
                    "name": "restaurant name",
                    "cuisine": "cuisine type",
                    "price_range": "$-$$$",
                    "location": "area/district",
                    "speciality": "must-try dish",
                    "atmosphere": "casual/fine dining/street food",
                    "estimated_cost_per_person": "cost range"
                }}
            ],
            "local_food_tips": [
                "tip 1 about local food culture",
                "tip 2 about local food culture"
            ],
            "food_districts": [
                "popular food area 1",
                "popular food area 2"
            ]
        }}
        Include at least 8-10 restaurants covering breakfast, lunch, dinner, and snacks.
        Include mix of budget-friendly and mid-range options.
        """
        
        response = self.model.generate_content(prompt)
        return self._parse_json_response(response.text)
    
    def generate_map_locations(self, city, activities):
        locations_text = ", ".join([activity.get('location', '') for activity in activities])
        
        prompt = f"""
        For the city {city}, provide coordinates for these locations: {locations_text}
        Return only a JSON object with this structure:
        {{
            "locations": [
                {{
                    "name": "location name",
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "type": "restaurant/attraction/hotel"
                }}
            ],
            "city_center": {{
                "latitude": 0.0,
                "longitude": 0.0
            }}
        }}
        Provide approximate coordinates if exact ones aren't known.
        """
        
        response = self.model.generate_content(prompt)
        return self._parse_json_response(response.text)
    
    def _parse_json_response(self, response_text):
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            return {"error": "Failed to parse response"}