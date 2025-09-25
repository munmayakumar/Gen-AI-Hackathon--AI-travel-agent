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
   pip install -r requirement.txt

2. Install MCP Servers:
   ```
    python setup_mcp_servers.py


3. Set Environment Variables:
   
   Copy .env.example to .env and fill in your API keys:

      - GEMINI_API_KEY - Get from Google AI Studio

      - GOOGLE_MAPS_API_KEY - Get from Google Cloud Console

      - GCP_PROJECT_ID - Your Google Cloud Project ID

      - BIGQUERY_DATASET - Your BigQuery dataset name

4. Run the Application:
   
   ```bash
   ./run.sh

5.GCP/BigQuery Setup

   1. Create BigQuery Dataset:
      
    CREATE SCHEMA IF NOT EXISTS travel_planner;
    
   2. Automatic Table Creation
      
     --  Tables will be automatically created when the application first runs.

6. File structure

 ## Project Structure

```
AI travel-planner/
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── run.sh                 # Startup script
├── setup_mcp_servers.py   # MCP server installation
├── .env.example           # Environment variables template
├── README.md              # Project documentation
├── src/                   # Source modules directory
├── user_manager.py        # User authentication and management
├── payment_gateway.py     # Payment processing
├── booking_services.py    # Booking management
└── itinerary_generator.py # AI itinerary generation
```



**API Keys Required**:

   - Google Gemini API

   - Google Maps API

   - Google Cloud Platform (for BigQuery)


 
## Key Improvements Made:

1. **Weather Integration**: Added weather forecast retrieval and activity recommendations based on weather conditions
2. **Natural Disaster Monitoring**: Added checks for disaster alerts with safety recommendations
3. **GCP/BigQuery Integration**: Modified all data storage to use BigQuery with proper table schemas
4. **Production Ready**: Replaced all placeholders with configurable environment variables
5. **Modular Structure**: Organized code into meaningful files and modules
6. **Error Handling**: Added robust error handling and fallback mechanisms
7. **Documentation**: Added comprehensive README with setup instructions

The code is now ready for GitLab configuration and GCP deployment. All database operations use BigQuery with the table name `travel_planner` as requested.
