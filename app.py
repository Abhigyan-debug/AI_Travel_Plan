import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import folium
from folium import plugins
import time

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(
    page_title="AI Travel Itinerary Generator",
    page_icon="✈️",
    layout="wide"
)

def parse_json_response(response_text):
    """Parse JSON response from Gemini with robust error handling"""
    try:
        # Clean the response text
        cleaned_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        
        cleaned_text = cleaned_text.strip()
        
        start_idx = cleaned_text.find('{')
        end_idx = cleaned_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_str = cleaned_text[start_idx:end_idx+1]
            return json.loads(json_str)
        else:
            # If no JSON found, return the text as a simple structure
            return {"content": cleaned_text, "error": "No valid JSON found"}
            
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {e}")
        return {"error": "Failed to parse JSON", "raw_text": response_text[:500]}
    except Exception as e:
        st.error(f"Unexpected error in parsing: {e}")
        return {"error": "Unexpected parsing error", "raw_text": response_text[:500]}

def generate_trip_summary(city, budget, days):
    """Generate trip summary with error handling"""
    try:
        prompt = f"""
        Create a travel summary for {city} with ${budget} budget for {days} days.
        Respond with ONLY a JSON object in this exact format:
        {{
            "city": "{city}",
            "total_budget": {budget},
            "duration": {days},
            "overview": "Brief overview of what to expect in {city}",
            "budget_breakdown": {{
                "accommodation": "30-40% of budget",
                "food": "25-35% of budget",
                "activities": "20-30% of budget",
                "transport": "10-15% of budget"
            }},
            "best_time": "Best months to visit",
            "currency": "Local currency",
            "highlights": ["Top attraction 1", "Top attraction 2", "Top attraction 3"]
        }}
        """
        
        response = model.generate_content(prompt)
        return parse_json_response(response.text)
        
    except Exception as e:
        st.error(f"Error generating trip summary: {e}")
        return {"error": f"API Error: {e}"}

def generate_daily_itinerary(city, day, budget_per_day):
    """Generate daily itinerary with error handling"""
    try:
        prompt = f"""
        Create day {day} itinerary for {city} with ${budget_per_day} daily budget.
        Respond with ONLY a JSON object in this format:
        {{
            "day": {day},
            "theme": "Day theme like 'Historical Sites' or 'Cultural Experience'",
            "activities": [
                {{
                    "time": "9:00 AM",
                    "activity": "Activity name",
                    "location": "Specific location",
                    "duration": "2 hours",
                    "cost": "$10-15",
                    "description": "Brief description"
                }},
                {{
                    "time": "11:30 AM",
                    "activity": "Next activity",
                    "location": "Location",
                    "duration": "1.5 hours", 
                    "cost": "$5-10",
                    "description": "Description"
                }}
            ],
            "meals": [
                {{
                    "time": "Breakfast",
                    "restaurant": "Restaurant name",
                    "dish": "Recommended dish",
                    "cost": "$8-12"
                }}
            ],
            "transportation": "How to get around",
            "total_cost": "Estimated total for the day"
        }}
        Include 4-5 activities and 3 meal suggestions.
        """
        
        response = model.generate_content(prompt)
        return parse_json_response(response.text)
        
    except Exception as e:
        st.error(f"Error generating day {day} itinerary: {e}")
        return {"error": f"API Error: {e}"}

def generate_dining_recommendations(city, budget_range):
    """Generate dining recommendations"""
    try:
        prompt = f"""
        Generate dining recommendations for {city} within {budget_range} budget.
        Respond with ONLY a JSON object in this format:
        {{
            "restaurants": [
                {{
                    "name": "Restaurant name",
                    "cuisine": "Cuisine type",
                    "price_range": "$-$$$",
                    "location": "Area/district",
                    "specialty": "Must-try dish",
                    "meal_type": "breakfast/lunch/dinner/snack",
                    "cost_per_person": "$10-15"
                }}
            ],
            "food_districts": ["Popular food area 1", "Popular food area 2"],
            "local_tips": ["Food tip 1", "Food tip 2"],
            "must_try": ["Local dish 1", "Local dish 2", "Local dish 3"]
        }}
        Include at least 8 restaurants covering all meal types and price ranges.
        """
        
        response = model.generate_content(prompt)
        return parse_json_response(response.text)
        
    except Exception as e:
        st.error(f"Error generating dining recommendations: {e}")
        return {"error": f"API Error: {e}"}

def create_simple_map(city):
    """Create a simple map for the city"""
    try:
        # Basic coordinates for some major cities (you can expand this)
        city_coords = {
            "delhi": [28.6139, 77.2090],
            "mumbai": [19.0760, 72.8777],
            "mathura": [27.4924, 77.6737],
            "lucknow": [26.8467, 80.9462],
            "paris": [48.8566, 2.3522],
            "tokyo": [35.6762, 139.6503],
            "new york": [40.7128, -74.0060],
            "london": [51.5074, -0.1278]
        }
        
        # Get coordinates for the city (default to Delhi if not found)
        coords = city_coords.get(city.lower(), [28.6139, 77.2090])
        
        # Create map
        m = folium.Map(location=coords, zoom_start=12)
        
        # Add a marker for the city center
        folium.Marker(
            coords,
            popup=f"{city.title()} - Your Destination",
            tooltip=f"Welcome to {city.title()}!",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        return m
        
    except Exception as e:
        st.error(f"Error creating map: {e}")
        return None

def main():
    st.title("🌍 AI Travel Itinerary Generator")
    st.markdown("**Create personalized travel itineraries with dining recommendations for any city!**")
    
    # Sidebar inputs
    with st.sidebar:
        st.header("🎯 Plan Your Trip")
        
        city = st.text_input("🏙️ Enter City", placeholder="e.g., Mathura, Delhi, Paris, Tokyo")
        budget = st.number_input("💰 Total Budget ($)", min_value=50, max_value=10000, value=500, step=50)
        days = st.number_input("📅 Number of Days", min_value=1, max_value=14, value=3)
        
        st.info("💡 **Indian Cities**: Try Mathura, Delhi, Mumbai, Lucknow!")
        
        generate_btn = st.button("🚀 Generate Itinerary", type="primary", use_container_width=True)
    
    if not api_key:
        st.error("⚠️ **Gemini API Key not found!** Please add your API key to the .env file.")
        st.code("GEMINI_API_KEY=your_api_key_here")
        return
    
    if generate_btn:
        if not city:
            st.warning("Please enter a city name!")
            return
        
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Generate Summary
            status_text.text("🔄 Step 1: Generating trip overview...")
            progress_bar.progress(20)
            
            summary = generate_trip_summary(city, budget, days)
            
            if "error" in summary:
                st.error(f"Error in summary generation: {summary.get('error', 'Unknown error')}")
                if "raw_text" in summary:
                    st.text(f"Raw response: {summary['raw_text']}")
                return
            
            # Step 2: Generate Daily Itineraries
            status_text.text("🔄 Step 2: Creating daily plans...")
            progress_bar.progress(40)
            
            daily_budget = budget / days
            daily_itineraries = []
            
            for day in range(1, days + 1):
                daily_plan = generate_daily_itinerary(city, day, daily_budget)
                daily_itineraries.append(daily_plan)
                time.sleep(0.5)  # Small delay to avoid rate limiting
            
            # Step 3: Generate Dining Recommendations
            status_text.text("🔄 Step 3: Finding best restaurants...")
            progress_bar.progress(70)
            
            budget_range = "budget-friendly" if daily_budget < 50 else "mid-range" if daily_budget < 150 else "luxury"
            dining = generate_dining_recommendations(city, budget_range)
            
            # Step 4: Create Map
            status_text.text("🔄 Step 4: Creating your map...")
            progress_bar.progress(90)
            
            city_map = create_simple_map(city)
            
            # Complete
            progress_bar.progress(100)
            status_text.text("✅ Your itinerary is ready!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            
            display_results(summary, daily_itineraries, dining, city_map, city, budget, days)
            
        except Exception as e:
            st.error(f"❌ **Unexpected Error**: {e}")
            st.info("💡 **Troubleshooting**: Try with a different city name or refresh the page.")
    
    else:
        # Show example when no generation is running
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("🇮🇳 **Indian Cities**\n\n- Mathura (Temples)\n- Delhi (History) \n- Mumbai (Bollywood)\n- Lucknow (Nawabi)")
        
        with col2:
            st.info("🌍 **International**\n\n- Paris (Romance)\n- Tokyo (Culture)\n- New York (Urban)\n- London (Royal)")
        
        with col3:
            st.info("💰 **Budget Tips**\n\n- $200-400: Budget travel\n- $500-800: Mid-range\n- $1000+: Luxury")

def display_results(summary, daily_itineraries, dining, city_map, city, budget, days):
    """Display all generated results"""
    
    # Trip Summary
    st.header(f"🎯 {city.title()} Trip Summary")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Budget", f"${budget}")
    with col2:
        st.metric("📅 Duration", f"{days} days")
    with col3:
        if summary.get("currency"):
            st.metric("💱 Currency", summary["currency"])
    with col4:
        if summary.get("best_time"):
            st.metric("🌤️ Best Time", summary["best_time"])
    
    # Overview
    if summary.get("overview"):
        st.write("**✨ Overview:**", summary["overview"])
    
    # Highlights
    if summary.get("highlights"):
        st.write("**🌟 Top Highlights:**")
        for highlight in summary["highlights"]:
            st.write(f"• {highlight}")
    
    st.markdown("---")
    
    # Daily Itineraries
    st.header("📅 Day-by-Day Itinerary")
    
    for daily in daily_itineraries:
        if "error" not in daily:
            with st.expander(f"Day {daily.get('day', 'N/A')} - {daily.get('theme', 'Explore')}", expanded=True):
                
                # Activities
                if daily.get("activities"):
                    st.subheader("🎯 Activities")
                    for activity in daily["activities"]:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.write(f"**⏰ {activity.get('time', 'Time')}**")
                        with col2:
                            st.write(f"**{activity.get('activity', 'Activity')}**")
                            st.write(f"📍 {activity.get('location', 'Location')}")
                            st.write(f"💵 {activity.get('cost', 'Cost')} | ⏱️ {activity.get('duration', 'Duration')}")
                            if activity.get('description'):
                                st.write(f"ℹ️ {activity['description']}")
                        st.write("---")
                
                # Meals
                if daily.get("meals"):
                    st.subheader("🍽️ Recommended Meals")
                    meal_cols = st.columns(len(daily["meals"]))
                    for idx, meal in enumerate(daily["meals"]):
                        with meal_cols[idx]:
                            st.write(f"**{meal.get('time', 'Meal')}**")
                            st.write(f"🏪 {meal.get('restaurant', 'Restaurant')}")
                            st.write(f"🍽️ {meal.get('dish', 'Dish')}")
                            st.write(f"💰 {meal.get('cost', 'Cost')}")
                
                # Transportation & Total
                col1, col2 = st.columns(2)
                with col1:
                    if daily.get("transportation"):
                        st.write(f"🚗 **Transport:** {daily['transportation']}")
                with col2:
                    if daily.get("total_cost"):
                        st.write(f"💰 **Daily Total:** {daily['total_cost']}")
    
    st.markdown("---")
    
    # Dining Recommendations
    st.header("🍽️ Best Restaurants & Food")
    
    if "error" not in dining and dining.get("restaurants"):
        
        # Organize restaurants by meal type
        breakfast_places = [r for r in dining["restaurants"] if r.get("meal_type") == "breakfast"]
        lunch_places = [r for r in dining["restaurants"] if r.get("meal_type") == "lunch"]
        dinner_places = [r for r in dining["restaurants"] if r.get("meal_type") == "dinner"]
        snack_places = [r for r in dining["restaurants"] if r.get("meal_type") == "snack"]
        
        # Breakfast
        if breakfast_places:
            st.subheader("🌅 Breakfast Spots")
            for place in breakfast_places[:3]:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{place.get('name', 'Restaurant')}**")
                    st.write(f"🍳 {place.get('cuisine', 'Cuisine')} | 📍 {place.get('location', 'Location')}")
                    st.write(f"⭐ Try: {place.get('specialty', 'House special')}")
                with col2:
                    st.metric("Price", place.get('price_range', 'N/A'))
                    st.write(f"💰 {place.get('cost_per_person', 'Cost')}")
        
        # Lunch  
        if lunch_places:
            st.subheader("🌞 Lunch Places")
            for place in lunch_places[:3]:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{place.get('name', 'Restaurant')}**")
                    st.write(f"🍽️ {place.get('cuisine', 'Cuisine')} | 📍 {place.get('location', 'Location')}")
                    st.write(f"⭐ Try: {place.get('specialty', 'House special')}")
                with col2:
                    st.metric("Price", place.get('price_range', 'N/A'))
                    st.write(f"💰 {place.get('cost_per_person', 'Cost')}")
        
        # Dinner
        if dinner_places:
            st.subheader("🌙 Dinner Restaurants")
            for place in dinner_places[:3]:
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{place.get('name', 'Restaurant')}**")
                    st.write(f"🍽️ {place.get('cuisine', 'Cuisine')} | 📍 {place.get('location', 'Location')}")
                    st.write(f"⭐ Try: {place.get('specialty', 'House special')}")
                with col2:
                    st.metric("Price", place.get('price_range', 'N/A'))
                    st.write(f"💰 {place.get('cost_per_person', 'Cost')}")
        
        # Additional Info
        col1, col2 = st.columns(2)
        
        with col1:
            if dining.get("food_districts"):
                st.subheader("🏙️ Popular Food Areas")
                for district in dining["food_districts"]:
                    st.write(f"• {district}")
        
        with col2:
            if dining.get("must_try"):
                st.subheader("🥘 Must-Try Local Dishes")
                for dish in dining["must_try"]:
                    st.write(f"• {dish}")
        
        if dining.get("local_tips"):
            st.subheader("💡 Local Food Tips")
            for tip in dining["local_tips"]:
                st.write(f"• {tip}")
    
    st.markdown("---")
    
    # Map
    if city_map:
        st.header("🗺️ Your Destination")
        st.components.v1.html(city_map._repr_html_(), height=400)

if __name__ == "__main__":
    main()
