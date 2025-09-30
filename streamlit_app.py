import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="SoccerStats2",
    page_icon="⚽",
    layout="wide"
)

# Main title
st.title("⚽ SoccerStats2")

# Welcome message
st.write("Welcome to SoccerStats2 - Your Soccer Statistics Dashboard!")

# Sidebar
st.sidebar.header("Navigation")
st.sidebar.info("This is a Streamlit application for soccer statistics.")

# Main content
st.header("Getting Started")
st.write("""
This is the main page of your SoccerStats2 application.
You can start building your soccer statistics dashboard here.
""")

# Example section
st.subheader("Features")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Teams", "0", help="Number of teams tracked")

with col2:
    st.metric("Matches", "0", help="Number of matches analyzed")

with col3:
    st.metric("Players", "0", help="Number of players in database")

# Footer
st.divider()
st.caption("SoccerStats2 - Powered by Streamlit")
