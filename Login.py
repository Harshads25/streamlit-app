import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time

# Function to fetch weather data from Open Meteo API
def fetch_weather_data():
    url = ('https://archive-api.open-meteo.com/v1/archive?latitude=21.1463&longitude=79.0849&start_date=2024-05-01&end_date=2024-09-04&hourly=soil_temperature_0_to_7cm&daily=temperature_2m_max,temperature_2m_min,rain_sum&timezone=auto')
    response = requests.get(url)
    data = response.json()
    daily_data = data['daily']
    df = pd.DataFrame(daily_data)
    df['time'] = pd.to_datetime(df['time'])
    return df

# Function to load price trend data
def load_price_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['Date'])
    return df

# Simulated user credentials (replace with real authentication system for production)
users = {"arthex@gmail.com": "Arthex123"}

# Login page
def login():
    st.markdown(
        """
        <style>
        body {
            background-color: #f0f2f6;
        }
        .login-title {
            font-size: 40px;
            font-weight: bold;
            color: #333;
        }
        .login-subtitle {
            font-size: 20px;
            color: #555;
            margin-top: -10px;
        }
        .login-input {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
            box-sizing: border-box;
            border: 2px solid #ccc;
            border-radius: 4px;
            font-size: 18px;
        }
        .login-btn {
            background-color: #4CAF50;
            color: white;
            padding: 15px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 18px;
            width: 100%;
        }
        .login-btn:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-title">Welcome to Arthex Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Please log in to continue</div>', unsafe_allow_html=True)

    email = st.text_input("Email", value="", key="email", help="Enter your team email")
    password = st.text_input("Password", type="password", value="", key="password", help="Enter your password")

    if st.button("Login"):
        if email in users and users[email] == password:
            st.session_state.logged_in = True  # Set the login state to True
            st.session_state.user_email = email  # Store the logged-in user's email
            st.success(f"Welcome, {email}!")
        else:
            st.error("Invalid email or password. Please try again.")

# Main dashboard function
def show_dashboard():
    # File path for price data, background, and logo
    price_data_file_path = "/Users/harshadshingde/Desktop/SIH/streamlit_app/excel_maharastra.csv"
    logo_path = "/Users/harshadshingde/Desktop/SIH/streamlit_app/Arthex.png"
    background_path = "/Users/harshadshingde/Desktop/SIH/streamlit_app/Bagraoud.jpg.avif"

    # Load price data
    price_df = load_price_data(price_data_file_path)

    # Initialize session state variables
    if "animation_running" not in st.session_state:
        st.session_state.animation_running = False

    # Set the page config to wide
    st.set_page_config(page_title="Climate Insights and Market Price Tracker", layout="wide")

    # Custom CSS for background and logo
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url('file://{background_path}');
            background-size: cover;
            background-position: center;
            height: 100vh;
            width: 100%;
        }}
        .logo {{
            position: fixed;
            top: 10px;
            right: 10px;
            width: 150px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display the logo
    st.image(logo_path, width=150, caption="Arthex", use_column_width=False)

    # Sidebar navigation
    st.sidebar.title("Dashboard")
    tabs = st.sidebar.radio("Choose a tab", ["Weather Data and Price Trends", "Cumulative Rain Effect on Price Trends"])

    # Animation controls
    animation_speed = st.sidebar.slider("Animation Speed (1-10)", 1, 10, 5)
    if st.sidebar.button("Start Animation"):
        st.session_state.animation_running = True
    if st.sidebar.button("Stop Animation"):
        st.session_state.animation_running = False

    # Dashboard logic
    if tabs == "Weather Data and Price Trends":
        st.title("Climate Insights and Market Price Tracker")

        # Fetch weather data
        st.write("Fetching weather data...")
        weather_df = fetch_weather_data()

        # Dropdown for weather data type
        weather_type = st.selectbox(
            "Select Weather Data Type",
            ["None", "Max Temperature (°C)", "Min Temperature (°C)", "Rainfall (mm)"], index=0
        )
        weather_mapping = {
            "Max Temperature (°C)": "temperature_2m_max",
            "Min Temperature (°C)": "temperature_2m_min",
            "Rainfall (mm)": "rain_sum"
        }
        selected_data = weather_mapping.get(weather_type)

        # Dropdown for commodity
        commodity = st.selectbox(
            "Select Commodity to View Price Trends",
            options=[col for col in price_df.columns if col != 'Date'],
            index=0
        )

        # Display combined data graph
        st.write("### Combined Weather and Price Data")
        plot_container = st.empty()

        combined_df = pd.DataFrame({
            'Date': weather_df['time'],
            'Weather': weather_df[selected_data] if selected_data else None,
            'Price': price_df[commodity].values[:len(weather_df)]
        })

        # Plot with secondary y-axis
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=combined_df['Date'], y=combined_df['Price'], mode='lines', name=f'Price of {commodity}', yaxis="y1", line=dict(color='blue')))
        if selected_data is not None:
            fig.add_trace(go.Scatter(x=combined_df['Date'], y=combined_df['Weather'], mode='lines', name=weather_type, yaxis="y2", line=dict(color='red')))

        fig.update_layout(
            width=1200, height=600, title='Price and Weather Trends with Separate Y-Axes',
            xaxis_title='Date',
            yaxis=dict(title='Price', titlefont=dict(color='blue'), tickfont=dict(color='blue')),
            yaxis2=dict(title=weather_type if selected_data else '', titlefont=dict(color='red'), tickfont=dict(color='red'), overlaying='y', side='right'),
            title_x=0.5
        )

        plot_container.plotly_chart(fig)

    elif tabs == "Cumulative Rain Effect on Price Trends":
        st.title("Cumulative Rain Effect on Price Trends")

        # Fetch weather data
        st.write("Fetching weather data...")
        weather_df = fetch_weather_data()

        # Calculate cumulative rainfall
        weather_df['cumulative_rain'] = weather_df['rain_sum'].cumsum()

        # Dropdown for commodity
        commodity = st.selectbox(
            "Select Commodity to View Price Trends",
            options=[col for col in price_df.columns if col != 'Date'],
            index=0
        )

        # Display cumulative rain effect on price graph
        st.write("### Cumulative Rainfall and Price Data")
        plot_container = st.empty()

        combined_df = pd.DataFrame({
            'Date': weather_df['time'],
            'Cumulative Rainfall': weather_df['cumulative_rain'],
            'Price': price_df[commodity].values[:len(weather_df)]
        })

        # Plot with secondary y-axis
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=combined_df['Date'], y=combined_df['Price'], mode='lines', name=f'Price of {commodity}', yaxis="y1", line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=combined_df['Date'], y=combined_df['Cumulative Rainfall'], mode='lines', name="Cumulative Rainfall", yaxis="y2", line=dict(color='red')))

        fig.update_layout(
            width=1200, height=600, title='Cumulative Rainfall and Price Trends',
            xaxis_title='Date',
            yaxis=dict(title='Price', titlefont=dict(color='blue'), tickfont=dict(color='blue')),
            yaxis2=dict(title='Cumulative Rainfall (mm)', titlefont=dict(color='red'), tickfont=dict(color='red'), overlaying='y', side='right'),
            title_x=0.5
        )

        plot_container.plotly_chart(fig)

        # Animation logic
        if st.session_state.animation_running:
            for i in range(1, len(combined_df)):
                fig.data[0].y = combined_df['Price'][:i]
                fig.data[1].y = combined_df['Cumulative Rainfall'][:i]
                plot_container.plotly_chart(fig)
                time.sleep(0.1 / animation_speed)

# Run login or dashboard based on session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    show_dashboard()
else:
    login()
