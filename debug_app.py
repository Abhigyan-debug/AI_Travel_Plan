import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(
    page_title="Debug Travel App",
    page_icon="🐛",
    layout="wide"
)

st.title("🐛 Debug Travel App")

# Sidebar
with st.sidebar:
    st.header("Input")
    city = st.text_input("City", value="Mathura")
    budget = st.number_input("Budget", value=500)
    days = st.number_input("Days", value=2)
    
    if st.button("Generate Simple Itinerary"):
        st.write("Button clicked!")
        
        try:
            with st.spinner("Generating..."):
                # Very simple prompt
                prompt = f"Create a simple 2-day travel plan for {city} with ${budget} budget. Just give me 3-4 activities and 2-3 restaurants. Keep it simple, no JSON needed."
                
                response = model.generate_content(prompt)
                
                st.success("✅ Generation complete!")
                
                # Show the response
                st.subheader(f"Travel Plan for {city}")
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

st.write("This is a simplified version to test if the basic generation works.")