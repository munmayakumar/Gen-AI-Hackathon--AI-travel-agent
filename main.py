# main.py
import streamlit as st
import asyncio
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.user_manager import UserManager
from src.payment_gateway import PaymentGateway
from src.booking_services import BookingServices
from src.itinenary_generator import ItineraryGenerator

# Page configuration
st.set_page_config(
    page_title="Advanced AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'itineraries' not in st.session_state:
    st.session_state.itineraries = []
if 'selected_itinerary' not in st.session_state:
    st.session_state.selected_itinerary = None
if 'booking_results' not in st.session_state:
    st.session_state.booking_results = {}
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0

# Initialize services
user_manager = UserManager()
payment_gateway = PaymentGateway()
booking_services = BookingServices()
itinerary_generator = ItineraryGenerator()

# Environment variables (would be set in production)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "your_gemini_api_key_here")
GOOGLE_MAPS_API_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY", "your_google_maps_api_key_here")

def login_register_page():
    """Login and registration page"""
    st.title("✈️ Advanced AI Travel Planner")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                user = user_manager.login(email, password)
                if user:
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
    
    with tab2:
        with st.form("register_form"):
            name = st.text_input("Full Name", key="register_name")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    user = user_manager.register(email, password, name)
                    if user:
                        st.session_state.user = user
                        st.success("Registration successful!")
                        st.rerun()
                    else:
                        st.error("Email already exists")

def itinerary_planner_page():
    """Main itinerary planning page"""
    st.title("✈️ Plan Your Trip")
    
    # User info sidebar
    with st.sidebar:
        st.header(f"Welcome, {st.session_state.user['name']}!")
        st.write(f"Email: {st.session_state.user['email']}")
        
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.itineraries = []
            st.session_state.selected_itinerary = None
            st.rerun()
        
        # Show booking history
        if st.session_state.user.get('booking_history'):
            st.subheader("Booking History")
            for booking in st.session_state.user['booking_history'][:3]:  # Show last 3
                st.write(f"📅 {booking.get('type', 'Booking')} - ${booking.get('price', 0)}")
    
    # Main planning form
    with st.form("trip_planning_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            destination = st.text_input("Destination", placeholder="e.g., Paris, France")
            start_date = st.date_input("Start Date", min_value=datetime.today())
            num_days = st.slider("Number of Days", 1, 30, 7)
        
        with col2:
            budget = st.slider("Budget (USD)", 500, 10000, 2000, step=100)
            travel_style = st.multiselect(
                "Travel Style",
                ["Adventure", "Luxury", "Budget", "Cultural", "Relaxation", "Food"],
                default=["Cultural"]
            )
            preferences = st.text_area("Additional Preferences", placeholder="e.g., Vegetarian food, wheelchair accessible")
        
        submitted = st.form_submit_button("Generate Itineraries")
        
        if submitted:
            if not destination:
                st.error("Please enter a destination")
            else:
                with st.spinner("Generating itineraries with AI... This may take a minute."):
                    # Generate itineraries
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        itineraries = loop.run_until_complete(
                            itinerary_generator.generate_itineraries(
                                destination=destination,
                                num_days=num_days,
                                preferences=preferences + " " + ", ".join(travel_style),
                                budget=budget,
                                gemini_key=GEMINI_API_KEY,
                                google_maps_key=GOOGLE_MAPS_API_KEY,
                                num_itineraries=3,
                                start_date=start_date
                            )
                        )
                        
                        st.session_state.itineraries = itineraries
                        st.session_state.destination = destination
                        st.session_state.start_date = start_date
                        st.success(f"Generated {len(itineraries)} itinerary options!")
                        
                    except Exception as e:
                        st.error(f"Error generating itineraries: {str(e)}")
                    finally:
                        loop.close()
    
    # Display generated itineraries
    if st.session_state.itineraries:
        st.header("Generated Itinerary Options")
        
        for i, itinerary in enumerate(st.session_state.itineraries):
            with st.expander(f"Option {i+1}: {itinerary.get('title', 'Itinerary')} - ${itinerary.get('total_cost', 0)}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader(itinerary.get('title', ''))
                    st.write(f"**Focus:** {itinerary.get('focus', '')}")
                    st.write(f"**Total Cost:** ${itinerary.get('total_cost', 0)}")
                    st.write(f"**Unique Feature:** {itinerary.get('unique_selling_point', '')}")
                    
                    # Weather considerations
                    st.info(f"🌤️ **Weather Notes:** {itinerary.get('weather_considerations', '')}")
                    
                    # Safety recommendations
                    if itinerary.get('safety_recommendations'):
                        st.warning(f"⚠️ **Safety:** {itinerary.get('safety_recommendations', '')}")
                
                with col2:
                    if st.button(f"Select Option {i+1}", key=f"select_{i}"):
                        st.session_state.selected_itinerary = itinerary
                        st.session_state.current_step = 1
                        st.rerun()
                
                # Flight options
                st.subheader("Flight Options")
                for flight in itinerary.get('flight_options', []):
                    st.write(f"✈️ {flight.get('airline', '')}: ${flight.get('price', 0)} - {flight.get('duration', '')}")
                
                # Accommodation options
                st.subheader("Accommodation Options")
                for hotel in itinerary.get('accommodation_options', []):
                    st.write(f"🏨 {hotel.get('name', '')}: ${hotel.get('price_per_night', 0)}/night (Rating: {hotel.get('rating', 0)}/5)")
                
                # Daily itinerary
                st.subheader("Daily Plan")
                for day, activities in itinerary.get('daily_itinerary', {}).items():
                    with st.expander(day):
                        for activity in activities:
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                st.write(f"⏰ {activity.get('start_time', '')}-{activity.get('end_time', '')}: {activity.get('name', '')}")
                                if activity.get('weather_alternative'):
                                    st.caption(f"🌧️ Alternative: {activity.get('weather_alternative')}")
                            with col_b:
                                st.write(f"${activity.get('cost', 0)}")

def booking_page():
    """Booking and payment page"""
    st.title("📋 Complete Your Booking")
    
    if not st.session_state.selected_itinerary:
        st.warning("Please select an itinerary first")
        st.session_state.current_step = 0
        st.rerun()
        return
    
    itinerary = st.session_state.selected_itinerary
    
    # Progress bar
    steps = ["Itinerary Selection", "Flight Booking", "Accommodation Booking", "Activities Booking", "Payment"]
    progress_value = min(max(st.session_state.current_step / (len(steps) - 1), 0.0), 1.0)
    progress = st.progress(progress_value)
    step_index = min(st.session_state.current_step, len(steps) - 1)
    st.caption(f"Step {step_index + 1} of {len(steps)}: {steps[step_index]}")
    
    # Step 0: Itinerary confirmation
    if st.session_state.current_step == 0:
        st.header("Review Your Itinerary")
        st.json(itinerary, expanded=False)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate and download iCal
            ical_data = itinerary_generator.generate_ical(
                itinerary, 
                st.session_state.destination, 
                st.session_state.start_date
            )
            st.download_button(
                label="📅 Download iCal",
                data=ical_data,
                file_name=f"itinerary_{st.session_state.destination.lower().replace(' ', '_')}.ics",
                mime="text/calendar"
            )
        
        with col2:
            # Generate and download PDF
            pdf_content = itinerary_generator.generate_pdf(itinerary, st.session_state.destination)
            st.download_button(
                label="📄 Download PDF",
                data=pdf_content,
                file_name=f"itinerary_{st.session_state.destination.lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        if st.button("Continue to Booking"):
            st.session_state.current_step = 1
            st.rerun()
    
    # Step 1: Flight booking
    elif st.session_state.current_step == 1:
        st.header("Book Your Flight")
        
        for i, flight in enumerate(itinerary.get('flight_options', [])):
            with st.expander(f"Flight Option {i+1}: {flight.get('airline', '')}"):
                st.write(f"**Price:** ${flight.get('price', 0)}")
                st.write(f"**Duration:** {flight.get('duration', '')}")
                st.write(f"**Dates:** {flight.get('dates', 'Flexible')}")
                
                if st.button(f"Book This Flight", key=f"flight_{i}"):
                    user_email = st.session_state.user['email'] if st.session_state.user else 'unknown'
                    result = booking_services.book_flight(
                        user_email,
                        itinerary.get('id', 'unknown'),
                        flight
                    )
                    
                    st.session_state.booking_results['flight'] = result
                    
                    if result.get('success'):
                        st.success(f"Flight booked! Confirmation: {result.get('confirmation', '')}")
                        st.session_state.current_step = 2
                        st.rerun()
                    else:
                        st.error(f"Booking failed: {result.get('error', 'Unknown error')}")
        
        if st.button("Skip Flight Booking", key="skip_flight"):
            st.session_state.current_step = 2
            st.rerun()
    
    # Step 2: Accommodation booking
    elif st.session_state.current_step == 2:
        st.header("Book Your Accommodation")
        
        for i, hotel in enumerate(itinerary.get('accommodation_options', [])):
            with st.expander(f"Hotel Option {i+1}: {hotel.get('name', '')}"):
                st.write(f"**Type:** {hotel.get('type', 'Hotel')}")
                st.write(f"**Price per night:** ${hotel.get('price_per_night', 0)}")
                st.write(f"**Total price:** ${hotel.get('total_price', 0)}")
                st.write(f"**Rating:** {hotel.get('rating', 0)}/5")
                st.write(f"**Location:** {hotel.get('location', 'Unknown')}")
                
                if st.button(f"Book This Hotel", key=f"hotel_{i}"):
                    user_email = st.session_state.user['email'] if st.session_state.user else 'unknown'
                    result = booking_services.book_hotel(
                        user_email,
                        itinerary.get('id', 'unknown'),
                        hotel
                    )
                    
                    st.session_state.booking_results['hotel'] = result
                    
                    if result.get('success'):
                        st.success(f"Hotel booked! Confirmation: {result.get('confirmation', '')}")
                        st.session_state.current_step = 3
                        st.rerun()
                    else:
                        st.error(f"Booking failed: {result.get('error', 'Unknown error')}")
        
        if st.button("Skip Hotel Booking", key="skip_hotel"):
            st.session_state.current_step = 3
            st.rerun()
    
    # Step 3: Activities booking
    elif st.session_state.current_step == 3:
        st.header("Book Your Activities")
        
        activities_to_book = []
        for day, day_activities in itinerary.get('daily_itinerary', {}).items():
            for activity in day_activities:
                if activity.get('cost', 0) > 0:  # Only show paid activities
                    activities_to_book.append({
                        'day': day,
                        'activity': activity
                    })
        
        if activities_to_book:
            for i, item in enumerate(activities_to_book):
                activity = item['activity']
                with st.expander(f"Activity: {activity.get('name', '')} ({item['day']})"):
                    st.write(f"**Time:** {activity.get('start_time', '')}-{activity.get('end_time', '')}")
                    st.write(f"**Location:** {activity.get('location', 'Unknown')}")
                    st.write(f"**Cost:** ${activity.get('cost', 0)}")
                    st.write(f"**Description:** {activity.get('description', '')}")
                    
                    if activity.get('weather_alternative'):
                        st.info(f"🌧️ Weather Alternative: {activity.get('weather_alternative')}")
                    
                    if st.button(f"Book This Activity", key=f"activity_{i}"):
                        user_email = st.session_state.user['email'] if st.session_state.user else 'unknown'
                        result = booking_services.book_activity(
                            user_email,
                            itinerary.get('id', 'unknown'),
                            activity
                        )
                        
                        if 'activities' not in st.session_state.booking_results:
                            st.session_state.booking_results['activities'] = []
                        
                        st.session_state.booking_results['activities'].append(result)
                        
                        if result.get('success'):
                            st.success(f"Activity booked! Confirmation: {result.get('confirmation', '')}")
                        else:
                            st.error(f"Booking failed: {result.get('error', 'Unknown error')}")
            
            if st.button("Continue to Payment", key="to_payment"):
                st.session_state.current_step = 4
                st.rerun()
        else:
            st.info("No bookable activities found in this itinerary.")
            if st.button("Continue to Payment", key="to_payment_no_activities"):
                st.session_state.current_step = 4
                st.rerun()
    
    # Step 4: Payment
    elif st.session_state.current_step == 4:
        st.header("Payment")
        
        # Calculate total cost
        total_cost = itinerary.get('total_cost', 0)
        
        # Show booking summary
        st.subheader("Booking Summary")
        
        if 'flight' in st.session_state.booking_results:
            flight = st.session_state.booking_results['flight']
            st.write(f"✈️ Flight: ${flight.get('price', 0)}")
        
        if 'hotel' in st.session_state.booking_results:
            hotel = st.session_state.booking_results['hotel']
            st.write(f"🏨 Hotel: ${hotel.get('price', 0)}")
        
        if 'activities' in st.session_state.booking_results:
            for activity in st.session_state.booking_results['activities']:
                if activity.get('success'):
                    st.write(f"🎯 Activity: ${activity.get('price', 0)}")
        
        st.write(f"**Total: ${total_cost}**")
        
        # Payment form
        with st.form("payment_form"):
            st.subheader("Payment Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
                card_holder = st.text_input("Card Holder Name")
            
            with col2:
                exp_date = st.text_input("Expiration Date", placeholder="MM/YY")
                cvv = st.text_input("CVV", type="password")
            
            agree_terms = st.checkbox("I agree to the terms and conditions")
            
            if st.form_submit_button("Process Payment"):
                if not all([card_number, card_holder, exp_date, cvv, agree_terms]):
                    st.error("Please fill all fields and agree to terms")
                else:
                    # Process payment
                    payment_result = payment_gateway.process_payment(
                        total_cost,
                        "mock_token",  # In real implementation, this would be a payment token
                        f"Travel booking for {st.session_state.destination}"
                    )
                    
                    if payment_result.get('success'):
                        st.success("Payment processed successfully!")
                        
                        # Add booking to user history
                        booking_data = {
                            'type': 'complete_package',
                            'destination': st.session_state.destination,
                            'itinerary_id': itinerary.get('id'),
                            'total_cost': total_cost,
                            'booking_date': datetime.now().isoformat(),
                            'payment_reference': payment_result.get('transaction_id')
                        }
                        
                        user_manager.add_booking_to_history(
                            st.session_state.user['email'],
                            booking_data
                        )
                        
                        # Update user preferences based on this booking
                        current_prefs = st.session_state.user.get('preferences', {})
                        current_prefs['last_destination'] = st.session_state.destination
                        current_prefs['preferred_budget'] = total_cost
                        current_prefs['travel_style'] = itinerary.get('focus', '').lower()
                        
                        user_manager.update_user_preferences(
                            st.session_state.user['email'],
                            current_prefs
                        )
                        
                        st.session_state.current_step = 5
                        st.rerun()
                    else:
                        st.error(f"Payment failed: {payment_result.get('error', 'Unknown error')}")
    
    # Step 5: Confirmation
    elif st.session_state.current_step == 5:
        st.header("🎉 Booking Confirmed!")
        st.balloons()
        
        st.success("Your travel booking has been confirmed and paid for successfully.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Destination", st.session_state.destination)
        with col2:
            st.metric("Total Cost", f"${itinerary.get('total_cost', 0)}")
        with col3:
            st.metric("Duration", f"{len(itinerary.get('daily_itinerary', {}))} days")
        
        if st.button("Plan Another Trip"):
            # Reset for new planning
            st.session_state.itineraries = []
            st.session_state.selected_itinerary = None
            st.session_state.booking_results = {}
            st.session_state.current_step = 0
            st.rerun()

def main():
    """Main application function"""
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.session_state.user is None:
        login_register_page()
    else:
        if st.session_state.current_step == 0:
            itinerary_planner_page()
        else:
            booking_page()

if __name__ == "__main__":
    main()