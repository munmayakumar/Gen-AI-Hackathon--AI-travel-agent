# src/payment_gateway.py
import random
import time
from typing import Dict, Any
from google.cloud import bigquery

class PaymentGateway:
    """Mock payment gateway that can be replaced with real providers"""
    
    def __init__(self, project_id: str = "your-gcp-project-id", dataset_id: str = "travel_planner"):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)
        self.supported_providers = ["stripe", "paypal", "square", "braintree"]
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure payments table exists"""
        payments_table_id = f"{self.project_id}.{self.dataset_id}.payments"
        payments_schema = [
            bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("amount", "FLOAT", mode="REQUIRED"),
            bigquery.SchemaField("currency", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("provider", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        try:
            table = bigquery.Table(payments_table_id, schema=payments_schema)
            self.client.create_table(table, exists_ok=True)
        except Exception as e:
            print(f"Error creating payments table: {e}")
    
    def process_payment(self, amount: float, token: str, description: str) -> Dict[str, Any]:
        """Process a payment using the available gateways"""
        # Simulate API call delay
        time.sleep(1.5)
        
        provider = random.choice(self.supported_providers)
        success = random.random() > 0.05  # 95% success rate for demo
        
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        
        if success:
            # Record payment in BigQuery
            payment_record = {
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": "USD",
                "description": description,
                "provider": provider,
                "status": "completed",
                "created_at": time.time()
            }
            
            table_id = f"{self.project_id}.{self.dataset_id}.payments"
            errors = self.client.insert_rows_json(table_id, [payment_record])
            
            if errors:
                print(f"Error recording payment: {errors}")
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": "USD",
                "description": description,
                "provider": provider,
                "timestamp": time.time()
            }
        else:
            return {
                "success": False,
                "error": "Payment declined by bank",
                "provider": provider
            }
    
    def refund_payment(self, transaction_id: str, amount: float = None) -> Dict[str, Any]:
        """Process a refund for a previous payment"""
        # Simulate API call delay
        time.sleep(1)
        
        success = random.random() > 0.1  # 90% success rate for demo
        
        if success:
            # Update payment status in BigQuery
            query = f"""
                UPDATE `{self.project_id}.{self.dataset_id}.payments`
                SET status = 'refunded'
                WHERE transaction_id = @transaction_id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("transaction_id", "STRING", transaction_id)
                ]
            )
            
            try:
                self.client.query(query, job_config=job_config).result()
            except Exception as e:
                print(f"Error updating payment status: {e}")
            
            return {
                "success": True,
                "refund_id": f"RFN{random.randint(100000, 999999)}",
                "transaction_id": transaction_id,
                "amount": amount or random.randint(50, 100),  # Simulated partial refund
                "message": "Refund processed successfully"
            }
        else:
            return {
                "success": False,
                "error": "Unable to process refund - please contact support"
            }