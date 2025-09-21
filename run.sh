#!/bin/bash
# run.sh
echo "Starting Advanced AI Travel Planner..."
echo "Installing requirements: pip install -r requirements.txt"
pip install -r requirements.txt
echo "Starting Streamlit application..."
streamlit run main.py --server.address=0.0.0.0 --server.port=8502