import folium
from folium import plugins

class MapService:
    def __init__(self):
        pass
    
    def create_itinerary_map(self, city_center, locations):
        # Create base map
        m = folium.Map(
            location=[city_center['latitude'], city_center['longitude']],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Color mapping for different types
        color_map = {
            'restaurant': 'red',
            'attraction': 'blue',
            'hotel': 'green',
            'shopping': 'purple',
            'transport': 'orange'
        }
        
        # Add markers for each location
        for i, location in enumerate(locations, 1):
            color = color_map.get(location.get('type', 'attraction'), 'blue')
            
            folium.Marker(
                location=[location['latitude'], location['longitude']],
                popup=folium.Popup(f"<b>{location['name']}</b><br>Type: {location.get('type', 'N/A')}", max_width=200),
                tooltip=location['name'],
                icon=folium.Icon(color=color, icon='info-sign'),
                number=i
            ).add_to(m)
        
        # Add marker numbering plugin
        plugins.MarkerCluster().add_to(m)
        
        return m