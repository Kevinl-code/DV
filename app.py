import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_option_menu import option_menu

# Sidebar using option_menu
def sidebar():
    selected = option_menu(
        menu_title="Main Menu",
        options=["Import Data", "Category", "Charts"],
        icons=["upload", "book", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "5px", "background-color": "#100909"},
            "icon": {"color": "white", "font-size": "25px"},
            "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "#D4242B"},
        },
    )
    return selected

# Front Page Function
def front_page():
    st.title("Welcome!")

    # Add custom CSS for animation
    st.markdown("""
    <style>
    @keyframes flickerAnimation {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    .animated-title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        animation: flickerAnimation 2s infinite;
        color: #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='animated-title'>Data Visualization Solution</div>", unsafe_allow_html=True)

    # Center-align the button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Get Started"):
            st.session_state.page = "main_menu"

# Function to upload and save data to SQLite
def upload_to_db(file, table_name):
    try:
        data = pd.read_excel(file)

        conn = sqlite3.connect("kevinw.db")
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        data.to_sql(table_name, conn, index=False, if_exists="replace")
        conn.commit()
        conn.close()
        return "Data uploaded successfully!"
    except Exception as e:
        return f"Error: {e}"

# Main application logic
if 'page' not in st.session_state:
    st.session_state.page = "front_page"
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = None
    st.session_state.chart_settings = None

if st.session_state.page == "front_page":
    front_page()
else:
    with st.sidebar:
        selected_page = sidebar()

    if selected_page == "Import Data":
        st.session_state.page = "Import Data"
    elif selected_page == "Category":
        st.session_state.page = "Category"
    elif selected_page == "Charts":
        st.session_state.page = "Charts"

    if st.session_state.page == "Import Data":
        st.title("Import Data")
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
        table_name = st.text_input("Enter table name", placeholder="data_table")

        if uploaded_file is not None and table_name:
            if st.button("Upload to Database"):
                result = upload_to_db(uploaded_file, table_name)
                st.success(result)

    elif st.session_state.page == "Category":
        st.title("Category")
        conn = sqlite3.connect("kevinw.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        table_names = [table[0] for table in tables]

        if table_names:
            selected_table = st.selectbox("Choose a category (table)", options=table_names)

            if selected_table:
                data = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
               #st.write(data)

                if 'year' in data.columns:
                    years = data['year'].dropna().unique().tolist()
                    years.sort()
                    years.insert(0, "All years")

                    year_selection = st.selectbox("Select year", years)

                    if year_selection != "All years":
                        data = data[data['year'] == year_selection]

                columns = [col for col in data.columns if col != 'year']
                selected_columns = st.multiselect("Select columns for visualization", columns, default=columns)
                chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Line Chart", "Bar Chart", "Column Chart"])

                if selected_columns:
                    x_axis = st.selectbox("Select X-axis", options=selected_columns)
                    y_axis = st.selectbox("Select Y-axis", options=[col for col in selected_columns if col != x_axis])

                    

                    if st.button("Generate Chart"):
                        if chart_type == "Pie Chart":
                            fig = px.pie(data, names=x_axis, values=y_axis, title="Pie Chart")
                        elif chart_type == "Line Chart":
                            fig = px.line(data, x=x_axis, y=y_axis, title="Line Chart")
                        elif chart_type == "Bar Chart":
                            fig = px.bar(data, x=x_axis, y=y_axis, title="Bar Chart")
                        elif chart_type == "Column Chart":
                            fig = px.bar(data, x=x_axis, y=y_axis, title="Column Chart", orientation='h')

                        st.session_state.chart_data = fig
                        st.session_state.chart_settings = selected_columns
                        st.session_state.page = "Charts"
        conn.close()

    elif st.session_state.page == "Charts":
        st.title("Charts")
        if st.session_state.chart_data and st.session_state.chart_settings:
           #st.write(st.session_state.chart_settings)
            columns = st.session_state.chart_settings
            selected_columns = st.multiselect("Select columns for visualization", columns, default=columns)
            st.plotly_chart(st.session_state.chart_data)
        else:
            st.warning("No chart data available. Please generate a chart in the 'Category' page.")
