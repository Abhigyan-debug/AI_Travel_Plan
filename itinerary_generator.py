from gemini_service import GeminiService
from map_service import MapService

class ItineraryGenerator:
    def __init__(self):
        self.gemini = GeminiService()
        self.map_service = MapService()
    
    def generate_complete_itinerary(self, city, budget, days):
        # Step 1: Generate overview and summary
        summary = self.gemini.generate_itinerary_summary(city, budget, days)
        
        # Step 2: Generate daily itineraries
        daily_budget = budget / days
        daily_itineraries = []
        all_activities = []
        
        for day in range(1, days + 1):
            daily_itinerary = self.gemini.generate_daily_itinerary(city, day, daily_budget)
            daily_itineraries.append(daily_itinerary)
            if 'activities' in daily_itinerary:
                all_activities.extend(daily_itinerary['activities'])
        
        # Step 3: Generate dining recommendations
        budget_range = self._determine_budget_range(budget, days)
        dining = self.gemini.generate_dining_recommendations(city, budget_range)
        
        # Step 4: Generate map with locations
        map_data = self.gemini.generate_map_locations(city, all_activities)
        
        # Step 5: Create interactive map
        if 'city_center' in map_data and 'locations' in map_data:
            itinerary_map = self.map_service.create_itinerary_map(
                map_data['city_center'], 
                map_data['locations']
            )
        else:
            itinerary_map = None
        
        return {
            'summary': summary,
            'daily_itineraries': daily_itineraries,
            'dining': dining,
            'map_data': map_data,
            'map': itinerary_map
        }
    
    def _determine_budget_range(self, total_budget, days):
        daily_budget = total_budget / days
        if daily_budget < 50:
            return "budget-friendly"
        elif daily_budget < 150:
            return "mid-range"
        else:
            return "luxury"