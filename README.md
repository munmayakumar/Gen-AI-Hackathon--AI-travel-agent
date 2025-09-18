# Advanced AI Travel Planner

A comprehensive travel planning application that uses AI to generate personalized itineraries with real-time booking capabilities, weather considerations, and natural disaster alerts.

## Features

- **AI-Powered Itinerary Generation**: Uses Gemini AI with MCP servers for real-time travel data
- **Weather Integration**: Considers weather forecasts and provides alternative plans
- **Natural Disaster Monitoring**: Checks for safety alerts at destinations
- **Multi-Provider Booking**: Integrates with Airbnb, Booking.com, Expedia, Skyscanner, and more
- **Payment Processing**: Mock payment gateway with multiple providers
- **User Management**: Complete authentication and preference tracking
- **Export Options**: iCal and PDF itinerary exports
- **BigQuery Integration**: All data stored in Google BigQuery

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt

2. Install MCP Servers:

   python setup_mcp_servers.py

<img width="783" height="646" alt="image" src="https://github.com/user-attachments/assets/3e89ea6e-e1c5-4f0c-a286-51300e8b89a5" />




 # File structure

 <img width="847" height="326" alt="image" src="https://github.com/user-attachments/assets/6f153ac3-3aa2-4d36-b319-d6fe250a6002" />


<img width="764" height="172" alt="image" src="https://github.com/user-attachments/assets/abc6e428-2bd1-4602-b1fd-a93ea832f681" />


 
## Key Improvements Made:

1. **Weather Integration**: Added weather forecast retrieval and activity recommendations based on weather conditions
2. **Natural Disaster Monitoring**: Added checks for disaster alerts with safety recommendations
3. **GCP/BigQuery Integration**: Modified all data storage to use BigQuery with proper table schemas
4. **Production Ready**: Replaced all placeholders with configurable environment variables
5. **Modular Structure**: Organized code into meaningful files and modules
6. **Error Handling**: Added robust error handling and fallback mechanisms
7. **Documentation**: Added comprehensive README with setup instructions

The code is now ready for GitLab configuration and GCP deployment. All database operations use BigQuery with the table name `travel_planner` as requested.
