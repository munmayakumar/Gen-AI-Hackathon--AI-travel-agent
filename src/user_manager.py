# src/user_manager.py
import json
import hashlib
import os
from typing import Dict, Any, Optional
from google.cloud import bigquery
from datetime import datetime

class UserManager:
    """Manage user authentication and data storage with BigQuery"""
    
    def __init__(self, project_id: str = None, dataset_id: str = None):
        import streamlit as st
        self.project_id = project_id or st.secrets.get("GCP_PROJECT_ID", "tonal-apex-471812-j2")
        self.dataset_id = dataset_id or st.secrets.get("BIGQUERY_DATASET", "travel_planner")
        print(f"UserManager using project_id: {self.project_id}, dataset_id: {self.dataset_id}")
        self.client = bigquery.Client(project=self.project_id)
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure BigQuery tables exist"""
        # Users table
        users_table_id = f"{self.project_id}.{self.dataset_id}.users"
        users_schema = [
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("password_hash", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("preferences", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        try:
            table = bigquery.Table(users_table_id, schema=users_schema)
            self.client.create_table(table, exists_ok=True)
        except Exception as e:
            print(f"Error creating users table: {e}")
        
        # Bookings table
        bookings_table_id = f"{self.project_id}.{self.dataset_id}.bookings"
        bookings_schema = [
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("booking_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("booking_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("booking_data", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        try:
            table = bigquery.Table(bookings_table_id, schema=bookings_schema)
            self.client.create_table(table, exists_ok=True)
        except Exception as e:
            print(f"Error creating bookings table: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, email: str, password: str, name: str) -> Optional[Dict[str, Any]]:
        """Register a new user"""
        # Check if user already exists
        query = f"""
            SELECT email 
            FROM `{self.project_id}.{self.dataset_id}.users` 
            WHERE email = @email
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email)
            ]
        )
        
        result = self.client.query(query, job_config=job_config).result()
        if result.total_rows > 0:
            return None
        
        # Insert new user
        user_data = {
            "email": email,
            "password_hash": self._hash_password(password),
            "name": name,
            "preferences": json.dumps({}),
            "created_at": datetime.utcnow().isoformat()
        }
        
        table_id = f"{self.project_id}.{self.dataset_id}.users"
        job = self.client.load_table_from_json([user_data], table_id)
        job.result()  # Wait for the job to complete
        errors = job.errors if hasattr(job, 'errors') else []
        if errors:
            print(f"Error inserting user: {errors}")
            return None
        # Return user data without password hash
        return {
            "email": email,
            "name": name,
            "authenticated": True
        }
    
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user"""
        query = f"""
            SELECT email, name, preferences
            FROM `{self.project_id}.{self.dataset_id}.users` 
            WHERE email = @email AND password_hash = @password_hash
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email),
                bigquery.ScalarQueryParameter("password_hash", "STRING", self._hash_password(password))
            ]
        )
        
        result = self.client.query(query, job_config=job_config).result()
        
        if result.total_rows == 0:
            return None
        
        for row in result:
            # Get booking history
            booking_history = self.get_booking_history(email)
            
            return {
                "email": row.email,
                "name": row.name,
                "booking_history": booking_history,
                "preferences": json.loads(row.preferences) if row.preferences else {},
                "authenticated": True
            }
        
        return None
    
    def update_user_preferences(self, email: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        query = f"""
            UPDATE `{self.project_id}.{self.dataset_id}.users`
            SET preferences = @preferences
            WHERE email = @email
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email),
                bigquery.ScalarQueryParameter("preferences", "STRING", json.dumps(preferences))
            ]
        )
        
        try:
            self.client.query(query, job_config=job_config).result()
            return True
        except Exception as e:
            print(f"Error updating preferences: {e}")
            return False
    
    def add_booking_to_history(self, email: str, booking_data: Dict[str, Any]) -> bool:
        """Add a booking to user's history"""
        booking_record = {
            "email": email,
            "booking_id": booking_data.get("booking_id", f"BK{datetime.utcnow().timestamp()}"),
            "booking_type": booking_data.get("type", "unknown"),
            "provider": booking_data.get("provider", "user"),
            "itinerary_id": booking_data.get("itinerary_id", "unknown"),
            "booking_data": json.dumps(booking_data),
            "status": booking_data.get("status", "confirmed"),
            "created_at": datetime.utcnow().isoformat()
        }
        
        table_id = f"{self.project_id}.{self.dataset_id}.bookings"
            # Use batch insert instead of streaming insert
        job = self.client.load_table_from_json([booking_record], table_id)
        job.result()  # Wait for job to complete
        errors = job.errors if hasattr(job, 'errors') else None
        return not errors
    
    def get_booking_history(self, email: str) -> list:
        """Get user's booking history"""
        query = f"""
            SELECT booking_data
            FROM `{self.project_id}.{self.dataset_id}.bookings` 
            WHERE email = @email
            ORDER BY created_at DESC
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email)
            ]
        )
        
        result = self.client.query(query, job_config=job_config).result()
        bookings = []
        
        for row in result:
            try:
                bookings.append(json.loads(row.booking_data))
            except json.JSONDecodeError:
                continue
        
        return bookings