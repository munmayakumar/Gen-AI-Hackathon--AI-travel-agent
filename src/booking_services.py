import json
# src/booking_services.py
import random
import time
from typing import Dict, Any
from google.cloud import bigquery

class BookingServices:
    def book_hotel(self, email: str, itinerary_id: str, hotel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Book a hotel using available providers"""
        # Simulate API call delay
        time.sleep(1)

        provider = random.choice(self.providers["hotels"])
        success = random.random() > 0.1  # 90% success rate for demo

        booking_id = f"HT{random.randint(10000, 99999)}"

        if success:
            booking_record = {
                "email": email,
                "booking_id": booking_id,
                "booking_type": "hotel",
                "provider": provider,
                "itinerary_id": itinerary_id,
                "booking_data": json.dumps(hotel_data),
                "status": "confirmed",
                "created_at": time.time()
            }

            table_id = f"{self.project_id}.{self.dataset_id}.bookings"
            job = self.client.load_table_from_json([booking_record], table_id)
            job.result()  # Wait for job to complete
            errors = job.errors if hasattr(job, 'errors') else []
            if errors:
                print(f"Error recording booking: {errors}")

            return {
                "success": True,
                "booking_id": booking_id,
                "confirmation": f"Hotel confirmed at {hotel_data.get('name', 'Unknown')} via {provider}",
                "price": hotel_data.get('total_price', 0),
                "provider": provider,
                "itinerary_id": itinerary_id
            }
        else:
            return {
                "success": False,
                "error": "No available hotels matching your criteria",
                "provider": provider
            }
    """Service for handling bookings with various providers"""
    
    def __init__(self, project_id: str = "tonal-apex-471812-j2", dataset_id: str = "travel_planner"):
        import streamlit as st
        self.project_id = project_id or st.secrets.get("GCP_PROJECT_ID", "tonal-apex-471812-j2")
        self.dataset_id = dataset_id or st.secrets.get("BIGQUERY_DATASET", "travel_planner")
        print(f"BookingServices using project_id: {self.project_id}, dataset_id: {self.dataset_id}")
        self.client = bigquery.Client(project=self.project_id)
        self.providers = {
            "flights": ["skyscanner", "google_flights", "expedia"],
            "hotels": ["booking", "expedia", "airbnb"],
            "activities": ["viator", "getyourguide", "airbnb_experiences"]
        }
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Force bookings table to have correct schema by deleting and recreating it"""
        bookings_table_id = f"{self.project_id}.{self.dataset_id}.bookings"
        bookings_schema = [
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("booking_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("booking_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("provider", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("itinerary_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("booking_data", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        try:
            # Try to delete the table if it exists
            self.client.delete_table(bookings_table_id, not_found_ok=True)
            print(f"Deleted existing table: {bookings_table_id}")
        except Exception as e:
            print(f"Error deleting bookings table: {e}")
        try:
            table = bigquery.Table(bookings_table_id, schema=bookings_schema)
            self.client.create_table(table)
            print(f"Created bookings table with correct schema: {bookings_table_id}")
        except Exception as e:
            print(f"Error creating bookings table: {e}")
    
    def book_flight(self, email: str, itinerary_id: str, flight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Book a flight using available providers"""
        # Simulate API call delay
        time.sleep(1)
        
        provider = random.choice(self.providers["flights"])
        success = random.random() > 0.1  # 90% success rate for demo
        
        booking_id = f"FL{random.randint(10000, 99999)}"
        
        if success:
            booking_record = {
                "email": email,
                "booking_id": booking_id,
                "booking_type": "flight",
                "provider": provider,
                "itinerary_id": itinerary_id,
                "booking_data": json.dumps(flight_data),
                "status": "confirmed",
                "created_at": time.time()
            }
            
            table_id = f"{self.project_id}.{self.dataset_id}.bookings"
            job = self.client.load_table_from_json([booking_record], table_id)
            job.result()  # Wait for the job to complete
            errors = job.errors if hasattr(job, 'errors') else []
            if errors:
                print(f"Error recording booking: {errors}")
            
            return {
                "success": True,
                "booking_id": booking_id,
                "confirmation": f"Flight confirmed with {flight_data.get('airline', 'Unknown')} via {provider}",
                "price": flight_data.get('price', 0),
                "provider": provider,
                "itinerary_id": itinerary_id
            }
        else:
            return {
                "success": False,
                "error": "No available flights matching your criteria",
                "provider": provider
            }
    
    def book_activity(self, email: str, itinerary_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Book an activity using available providers"""
        # Simulate API call delay
        time.sleep(0.5)

        provider = random.choice(self.providers["activities"])
        success = random.random() > 0.1  # 90% success rate for demo

        booking_id = f"AC{random.randint(10000, 99999)}"

        if success:
            booking_record = {
                "email": email,
                "booking_id": booking_id,
                "booking_type": "activity",
                "provider": provider,
                "itinerary_id": itinerary_id,
                "booking_data": json.dumps(activity_data),
                "status": "confirmed",
                "created_at": time.time()
            }

            table_id = f"{self.project_id}.{self.dataset_id}.bookings"
            job = self.client.load_table_from_json([booking_record], table_id)
            job.result()  # Wait for job to complete
            errors = job.errors if hasattr(job, 'errors') else None

            if errors:
                print(f"Error recording booking: {errors}")

            return {
                "success": True,
                "booking_id": booking_id,
                "confirmation": f"Activity confirmed: {activity_data.get('name', 'Unknown')} via {provider}",
                "price": activity_data.get('cost', 0),
                "itinerary_id": itinerary_id
            }
        else:
            return {
                "success": False,
                "error": "No available activities matching your criteria",
                "provider": provider
            }
    def book_activity(self, email: str, itinerary_id: str, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Book an activity using available providers"""
        # Simulate API call delay
        time.sleep(0.5)
        
        provider = random.choice(self.providers["activities"])
        success = random.random() > 0.1  # 90% success rate for demo
        booking_id = f"AC{random.randint(10000, 99999)}"
        
        if success:
            booking_record = {
                "email": email,
                "booking_id": booking_id,
                "booking_type": "activity",
                "provider": provider,
                "itinerary_id": itinerary_id,
                "booking_data": json.dumps(activity_data),
                "status": "confirmed",
                "created_at": time.time()
            }
            
            table_id = f"{self.project_id}.{self.dataset_id}.bookings"
            # Use batch insert instead of streaming insert
            job = self.client.load_table_from_json([booking_record], table_id)
            job.result()  # Wait for job to complete
            errors = job.errors if hasattr(job, 'errors') else None
            
            if errors:
                print(f"Error recording booking: {errors}")
            
            return {
                "success": True,
                "booking_id": booking_id,
                "confirmation": f"Activity confirmed: {activity_data.get('name', 'Unknown')} via {provider}",
                "price": activity_data.get('cost', 0),
                "provider": provider,
                "itinerary_id": itinerary_id
            }
        else:
            return {
                "success": False,
                "error": "Activity not available for the selected dates",
                "provider": provider
            }
    
    def cancel_booking(self, booking_id: str, booking_type: str) -> Dict[str, Any]:
        """Cancel a booking"""
        # Simulate API call delay
        time.sleep(1)
        
        success = random.random() > 0.2  # 80% success rate for demo
        
        if success:
            # Update booking status in BigQuery
            query = f"""
                UPDATE `{self.project_id}.{self.dataset_id}.bookings`
                SET status = 'cancelled'
                WHERE booking_id = @booking_id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("booking_id", "STRING", booking_id)
                ]
            )
            
            try:
                self.client.query(query, job_config=job_config).result()
            except Exception as e:
                print(f"Error updating booking status: {e}")
            
            return {
                "success": True,
                "message": f"{booking_type.capitalize()} booking {booking_id} successfully cancelled",
                "refund_amount": random.randint(50, 100)  # Simulated partial refund
            }
        else:
            return {
                "success": False,
                "error": "Unable to cancel booking - please contact customer service"
            }