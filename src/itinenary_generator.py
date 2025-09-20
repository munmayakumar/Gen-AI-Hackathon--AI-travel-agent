# src/itinerary_generator.py
import re
import random
import asyncio
import json
import requests
from textwrap import dedent
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from agno.agent import Agent
from agno.tools.mcp import MultiMCPTools
from agno.tools.googlesearch import GoogleSearchTools
class GeminiChat:
    """Custom GeminiChat class for Google Gemini API integration."""
    def __init__(self, id: str, api_key: str):
        self.id = id
        self.api_key = api_key

    async def arun(self, prompt: str):
        # This is a placeholder for async Gemini API call
        # Replace with actual Gemini API integration as needed
        import aiohttp
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.id}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                result = await resp.json()
                # Extract the generated content from Gemini response
                content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                class Response:
                    def __init__(self, content):
                        self.content = content
                return Response(content)
from typing import List, Dict, Any

class ItineraryGenerator:
    def __init__(self):
        self.mcp_tools = None
    
    async def connect_mcp_servers(self, google_maps_key: str = ""):
        """Connect to MCP servers for travel data"""
        try:
            self.mcp_tools = MultiMCPTools(
                [
                    "npx -y @modelcontextprotocol/server-airbnb --ignore-robots-txt",
                    "npx -y @modelcontextprotocol/server-booking",
                    "npx -y @modelcontextprotocol/server-expedia",
                    "npx -y @modelcontextprotocol/server-skyscanner",
                    "npx -y @modelcontextprotocol/server-google-flights",
                    "npx -y @modelcontextprotocol/server-viator",
                    "npx -y @modelcontextprotocol/server-getyourguide",
                ],
                env={"GOOGLE_MAPS_API_KEY": google_maps_key} if google_maps_key else {},
                timeout_seconds=60,
            )
            await self.mcp_tools.connect()
            return True
        except Exception as e:
            print(f"Error connecting to MCP servers: {e}")
            return False
    
    def _get_weather_forecast(self, destination: str, start_date: datetime, num_days: int) -> Dict[str, Any]:
        """Get weather forecast for destination (mock implementation)"""
        # In a real implementation, this would call a weather API
        weather_conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Stormy"]
        temperatures = {
            "Sunny": (75, 95),
            "Partly Cloudy": (70, 85),
            "Cloudy": (65, 80),
            "Rainy": (60, 75),
            "Stormy": (55, 70)
        }
        
        forecast = {}
        current_date = start_date
        
        for i in range(num_days):
            condition = random.choice(weather_conditions)
            temp_range = temperatures[condition]
            forecast[current_date.strftime("%Y-%m-%d")] = {
                "condition": condition,
                "high": random.randint(temp_range[0], temp_range[1]),
                "low": random.randint(temp_range[0] - 15, temp_range[1] - 10),
                "recommendations": self._get_weather_recommendations(condition)
            }
            current_date += timedelta(days=1)
        
        return forecast
    
    def _get_weather_recommendations(self, condition: str) -> List[str]:
        """Get activity recommendations based on weather"""
        recommendations = {
            "Sunny": [
                "Perfect day for outdoor activities",
                "Don't forget sunscreen and a hat",
                "Great day for beach or water activities"
            ],
            "Partly Cloudy": [
                "Good day for outdoor activities",
                "Might want to bring a light jacket",
                "Comfortable conditions for sightseeing"
            ],
            "Cloudy": [
                "Good day for outdoor activities without strong sun",
                "Might want to have indoor alternatives planned",
                "Comfortable temperatures for walking tours"
            ],
            "Rainy": [
                "Plan indoor activities or bring rain gear",
                "Consider museums, galleries, or indoor markets",
                "Check if outdoor activities have rain dates"
            ],
            "Stormy": [
                "Avoid outdoor activities if possible",
                "Consider rescheduling outdoor plans",
                "Have indoor backup plans ready"
            ]
        }
        return recommendations.get(condition, ["Check local weather advisories"])
    
    def _check_natural_disasters(self, destination: str, start_date: datetime) -> List[str]:
        """Check for natural disasters at destination (mock implementation)"""
        # In a real implementation, this would call disaster monitoring APIs
        disasters = [
            "No significant natural disasters reported",
            "Minor earthquake activity reported in the region",
            "Tropical storm warning in effect",
            "Wildfire risk elevated due to dry conditions",
            "Flood watch in effect for low-lying areas"
        ]
        
        # Higher probability of disasters for certain destinations
        disaster_prone = ["Japan", "Indonesia", "Philippines", "California", "Florida"]
        has_disaster = any(prone in destination for prone in disaster_prone) and random.random() > 0.7
        
        if has_disaster:
            return [random.choice(disasters[1:])]
        else:
            return [disasters[0]]
    
    async def generate_itineraries(self, destination: str, num_days: int, preferences: str, 
                                 budget: int, gemini_key: str, google_maps_key: str,
                                 num_itineraries: int = 3, start_date: datetime = None) -> List[Dict[str, Any]]:
        """Generate multiple itinerary options using AI and MCP servers"""
        
        try:
            # Get weather and disaster information
            start_date = start_date or datetime.now()
            weather_forecast = self._get_weather_forecast(destination, start_date, num_days)
            disaster_alerts = self._check_natural_disasters(destination, start_date)
            
            # Connect to MCP servers
            connected = await self.connect_mcp_servers(google_maps_key)
            if not connected:
                return self._generate_fallback_itineraries(destination, num_days, preferences, budget, num_itineraries, start_date)
            
            # Create travel planner agent
            travel_planner = Agent(
                name="Travel Planner",
                role="Creates travel itineraries using multiple data sources",
                model=GeminiChat(id="gemini-1.5-pro", api_key=gemini_key),
                description=dedent(
                    """\
                    You are a professional travel consultant AI that creates detailed, budget-conscious travel itineraries.
                    You have access to real-time data through MCP servers for accommodations, flights, and activities.
                    Consider weather conditions and natural disaster alerts when planning itineraries.
                    """
                ),
                instructions=[
                    "Create multiple itinerary options with different focuses (e.g., adventure, luxury, budget, cultural)",
                    "Include flight options, hotel recommendations, and daily activities",
                    "Provide detailed pricing breakdowns for each option",
                    "Ensure the total cost stays within the user's budget",
                    "Include practical information like transportation options and timing",
                    "Use data from MCP servers to get real-time availability and pricing",
                    "Consider weather forecasts and adjust activities accordingly",
                    "Include safety recommendations based on natural disaster alerts",
                    "Provide alternative indoor activities for bad weather days"
                ],
                tools=[self.mcp_tools, GoogleSearchTools()],
                add_datetime_to_instructions=True,
                markdown=True,
                show_tool_calls=False,
            )

            prompt = f"""
            Create {num_itineraries} different travel itinerary options for:
            **Destination:** {destination}
            **Duration:** {num_days} days
            **Start Date:** {start_date.strftime('%Y-%m-%d')}
            **Budget:** ${budget} USD total
            **Preferences:** {preferences}

            **Weather Forecast:**
            {json.dumps(weather_forecast, indent=2)}

            **Natural Disaster Alerts:**
            {json.dumps(disaster_alerts, indent=2)}

            For each itinerary option, provide:
            1. A descriptive title and focus (e.g., "Luxury Getaway", "Budget Adventure")
            2. Flight options with pricing (use MCP servers for real data)
            3. Accommodation options with pricing (use MCP servers for real data)
            4. Daily itinerary with activities, timing, and costs (use MCP servers for real data)
            5. Total estimated cost (must be under ${budget})
            6. A unique selling point for this itinerary
            7. Weather considerations and alternative plans
            8. Safety recommendations based on disaster alerts

            Return the response as a JSON array with each itinerary having the following structure:
            {{
              "id": "unique_id",
              "title": "Itinerary title",
              "focus": "e.g., Luxury, Budget, Adventure, Cultural",
              "description": "Detailed description",
              "total_cost": 0,
              "weather_considerations": "Notes about weather and alternative plans",
              "safety_recommendations": "Notes about safety based on disaster alerts",
              "flight_options": [
                {{
                  "airline": "Airline name",
                  "price": 0,
                  "duration": "Flight duration",
                  "dates": "Travel dates",
                  "source": "Data source"
                }}
              ],
              "accommodation_options": [
                {{
                  "name": "Hotel name",
                  "type": "Hotel/Airbnb",
                  "price_per_night": 0,
                  "total_price": 0,
                  "rating": 0,
                  "location": "Location details",
                  "source": "Data source"
                }}
              ],
              "daily_itinerary": {{
                "Day 1": [
                  {{
                    "name": "Activity name",
                    "description": "Activity details",
                    "start_time": "09:00",
                    "end_time": "12:00",
                    "location": "Activity location",
                    "cost": 0,
                    "source": "Data source",
                    "weather_alternative": "Alternative activity if weather is bad"
                  }}
                ]
              }},
              "unique_selling_point": "What makes this itinerary special"
            }}
            """

            response = await travel_planner.arun(prompt)
            
            # Parse the JSON response
            try:
                json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if json_match:
                    itineraries = json.loads(json_match.group())
                    return itineraries
                else:
                    # Fallback: try to parse the whole response
                    return json.loads(response.content)
            except json.JSONDecodeError:
                print("Failed to parse JSON response from AI, using fallback")
                return self._generate_fallback_itineraries(destination, num_days, preferences, budget, num_itineraries, start_date)

        except Exception as e:
            print(f"Error generating itineraries: {e}")
            return self._generate_fallback_itineraries(destination, num_days, preferences, budget, num_itineraries, start_date)
    
    def _generate_fallback_itineraries(self, destination: str, num_days: int, preferences: str, 
                                     budget: int, num_itineraries: int = 3, start_date: datetime = None) -> List[Dict[str, Any]]:
        """Generate fallback itineraries when MCP servers are unavailable"""
        import random
        import uuid
        
        # Get weather and disaster information for fallback
        start_date = start_date or datetime.now()
        weather_forecast = self._get_weather_forecast(destination, start_date, num_days)
        disaster_alerts = self._check_natural_disasters(destination, start_date)
        
        focuses = ["Luxury", "Budget", "Adventure", "Cultural", "Relaxation", "Food"]
        airlines = ["Delta", "United", "American", "Southwest", "JetBlue"]
        hotels = ["Marriott", "Hilton", "Hyatt", "InterContinental", "Holiday Inn"]
        activities = {
            "Adventure": ["Zip Lining", "Hiking", "White Water Rafting", "Rock Climbing"],
            "Cultural": ["Museum Tour", "Historical Site", "Local Market", "Traditional Show"],
            "Relaxation": ["Spa Day", "Beach Time", "Yoga Session", "Meditation"],
            "Food": ["Cooking Class", "Food Tour", "Wine Tasting", "Local Restaurant"]
        }
        
        indoor_alternatives = {
            "Zip Lining": "Indoor rock climbing",
            "Hiking": "Museum visit",
            "White Water Rafting": "Indoor water park",
            "Rock Climbing": "Indoor rock climbing gym",
            "Beach Time": "Spa day",
            "Yoga Session": "Indoor yoga studio",
            "Meditation": "Wellness center visit"
        }
        
        itineraries = []
        for i in range(num_itineraries):
            focus = random.choice(focuses)
            flight_price = random.randint(200, 600)
            hotel_price_per_night = random.randint(80, 300)
            total_cost = flight_price + (hotel_price_per_night * num_days)
            
            # Adjust to fit budget if needed
            if total_cost > budget * 0.9:
                scale = (budget * 0.9) / total_cost
                flight_price = int(flight_price * scale)
                hotel_price_per_night = int(hotel_price_per_night * scale)
                total_cost = flight_price + (hotel_price_per_night * num_days)
            
            itinerary = {
                "id": str(uuid.uuid4()),
                "title": f"{focus} {destination} Experience",
                "focus": focus,
                "description": f"A {num_days}-day {focus.lower()} trip to {destination} focusing on {preferences}",
                "total_cost": total_cost,
                "weather_considerations": "Check local weather forecast and plan accordingly. Have indoor alternatives ready.",
                "safety_recommendations": " ".join(disaster_alerts),
                "flight_options": [
                    {
                        "airline": random.choice(airlines),
                        "price": flight_price,
                        "duration": f"{random.randint(2, 8)}h {random.randint(0, 59)}m",
                        "dates": "Flexible dates",
                        "source": "Fallback data"
                    }
                ],
                "accommodation_options": [
                    {
                        "name": f"{random.choice(hotels)} {destination}",
                        "type": "Hotel",
                        "price_per_night": hotel_price_per_night,
                        "total_price": hotel_price_per_night * num_days,
                        "rating": round(random.uniform(3.5, 5.0), 1),
                        "location": "City Center",
                        "source": "Fallback data"
                    }
                ],
                "daily_itinerary": {},
                "unique_selling_point": f"Perfect for travelers seeking a {focus.lower()} experience"
            }
            
            # Generate daily activities
            current_date = start_date
            for day in range(1, num_days + 1):
                day_activities = []
                date_str = current_date.strftime("%Y-%m-%d")
                weather = weather_forecast.get(date_str, {"condition": "Sunny", "recommendations": ["Good weather for outdoor activities"]})
                
                for j in range(2):  # 2 activities per day
                    activity_type = focus if focus in activities else random.choice(list(activities.keys()))
                    activity_name = random.choice(activities[activity_type])
                    
                    # Add weather alternative for outdoor activities
                    weather_alternative = ""
                    if activity_name in indoor_alternatives and weather["condition"] in ["Rainy", "Stormy"]:
                        weather_alternative = indoor_alternatives[activity_name]
                    
                    day_activities.append({
                        "name": activity_name,
                        "description": f"Enjoy a {activity_name.lower()} experience in {destination}",
                        "start_time": f"{9 + j*4}:00",
                        "end_time": f"{12 + j*4}:00",
                        "location": f"{destination} City Center",
                        "cost": random.randint(20, 100),
                        "source": "Fallback data",
                        "weather_alternative": weather_alternative
                    })
                
                itinerary["daily_itinerary"][f"Day {day}"] = day_activities
                current_date += timedelta(days=1)
            
            itineraries.append(itinerary)
        
        return itineraries
    
    def generate_ical(self, itinerary: Dict[str, Any], destination: str, start_date: datetime) -> bytes:
        """Generate iCalendar file for the itinerary"""
        cal = Calendar()
        cal.add('prodid', f'-//Travel Planner//{destination}//EN')
        cal.add('version', '2.0')
        
        current_date = start_date
        
        for day, activities in itinerary.get('daily_itinerary', {}).items():
            for activity in activities:
                event = Event()
                event.add('summary', activity.get('name', 'Activity'))
                event.add('description', activity.get('description', ''))
                
                # Parse start and end times
                start_time_str = activity.get('start_time', '09:00')
                end_time_str = activity.get('end_time', '12:00')
                
                # Create datetime objects
                start_dt = datetime.combine(current_date, datetime.strptime(start_time_str, '%H:%M').time())
                end_dt = datetime.combine(current_date, datetime.strptime(end_time_str, '%H:%M').time())
                
                event.add('dtstart', start_dt)
                event.add('dtend', end_dt)
                event.add('location', activity.get('location', destination))
                
                cal.add_component(event)
            
            current_date += timedelta(days=1)
        
        return cal.to_ical()
    
    def generate_pdf(self, itinerary: Dict[str, Any], destination: str) -> str:
        """Generate PDF content for the itinerary (simplified)"""
        # In a real implementation, this would use a PDF generation library
        content = f"""
        TRAVEL ITINERARY FOR {destination.upper()}
        ===========================================
        
        Title: {itinerary.get('title', '')}
        Focus: {itinerary.get('focus', '')}
        Total Cost: ${itinerary.get('total_cost', 0)}
        
        Weather Considerations:
        {itinerary.get('weather_considerations', '')}
        
        Safety Recommendations:
        {itinerary.get('safety_recommendations', '')}
        
        FLIGHT OPTIONS:
        """
        
        for flight in itinerary.get('flight_options', []):
            content += f"""
            - {flight.get('airline', '')}: ${flight.get('price', 0)}
              Duration: {flight.get('duration', '')}
              Dates: {flight.get('dates', '')}
            """
        
        content += """
        ACCOMMODATION OPTIONS:
        """
        
        for hotel in itinerary.get('accommodation_options', []):
            content += f"""
            - {hotel.get('name', '')} ({hotel.get('type', '')})
              ${hotel.get('price_per_night', 0)}/night, Total: ${hotel.get('total_price', 0)}
              Rating: {hotel.get('rating', 0)}/5
              Location: {hotel.get('location', '')}
            """
        
        content += """
        DAILY ITINERARY:
        """
        
        for day, activities in itinerary.get('daily_itinerary', {}).items():
            content += f"""
            {day.upper()}:
            """
            for activity in activities:
                content += f"""
            - {activity.get('start_time', '')}-{activity.get('end_time', '')}: {activity.get('name', '')}
              Cost: ${activity.get('cost', 0)}
              Location: {activity.get('location', '')}
              {f'Weather Alternative: {activity.get("weather_alternative", "")}' if activity.get('weather_alternative') else ''}
                """
        
        content += f"""
        Unique Selling Point: {itinerary.get('unique_selling_point', '')}
        """
        
        return content