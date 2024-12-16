import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt

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
    st.markdown(
        """
        <style>
        .background {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            background-image: url('https://wallup.net/wp-content/uploads/2019/09/902450-electronics-machine-technology-circuit-electronic-computer-technics-detail-psychedelic-abstract-pattern.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        .title {
            font-size: 2.0rem;
            font-weight: bold;
            text-align: center;
            color: rgb(248, 252, 255);
        }
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
            color: rgb(147, 40, 85);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='background'></div>", unsafe_allow_html=True)
    st.markdown("<div class='title'>Welcome!</div>", unsafe_allow_html=True)
    st.markdown("<div class='animated-title'>Data Visualization Solution for Recent Trends in CS Technology</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([5, 3, 5])
    with col2:
        if st.button("Get Started"):
            st.session_state.page = "main_menu"

# Upload and save data to SQLite
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

# Axis Formatting Options
def get_axis_options(chart_type):
    options = {}
    options['font_size'] = st.number_input("Font size:", min_value=8, max_value=24, value=12, step=1)
    options['font_color'] = st.color_picker("Pick font color:", "#000000")
    options['grid'] = st.checkbox("Show grid", value=True)

    if chart_type != "Pie Chart":
        options['x_range'] = st.text_area("Enter X-axis range (comma-separated, e.g., min,max):")
        options['y_range'] = st.text_area("Enter Y-axis range (comma-separated, e.g., min,max):")

    return options

# Generate Chart
def generate_chart(chart_type, data, x_axis, y_axis, options):
    try:
        if chart_type == "Pie Chart":
            fig = px.pie(data, names=x_axis, values=y_axis, title="Pie Chart")
        elif chart_type == "Line Chart":
            fig = px.line(data, x=x_axis, y=y_axis, title="Line Chart")
        elif chart_type == "Bar Chart":
            fig = px.bar(data, x=x_axis, y=y_axis, title="Bar Chart")
        elif chart_type == "Column Chart":
            fig = px.bar(data, x=x_axis, y=y_axis, title="Column Chart", orientation='h')

        fig.update_layout(
            font=dict(size=options['font_size'], color=options['font_color']),
            xaxis=dict(gridcolor="gray" if options['grid'] else None, range=eval(options['x_range']) if options['x_range'] else None),
            yaxis=dict(gridcolor="gray" if options['grid'] else None, range=eval(options['y_range']) if options['y_range'] else None),
        )

        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error generating chart: {e}")

# Main application logic
if 'page' not in st.session_state:
    st.session_state.page = "front_page"

if st.session_state.page == "front_page":
    front_page()
else:
    with st.sidebar:
        selected_page = sidebar()

    if selected_page == "Import Data":
        st.title("Import Data")
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
        table_name = st.text_input("Enter table name", placeholder="data_table")

        if uploaded_file and table_name:
            if st.button("Upload to Database"):
                result = upload_to_db(uploaded_file, table_name)
                st.success(result)

    elif selected_page == "Category":
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
                chart_type = st.selectbox("Select Chart Type", ["Pie Chart", "Line Chart", "Bar Chart", "Column Chart"])
                x_axis = st.selectbox("Select X-axis", options=data.columns)
                y_axis = st.selectbox("Select Y-axis", options=[col for col in data.columns if col != x_axis])

                axis_options = get_axis_options(chart_type)

                if st.button("Generate Chart"):
                    st.session_state.chart_data = (chart_type, data, x_axis, y_axis, axis_options)
                    st.session_state.page = "Charts"
        conn.close()

    elif selected_page == "Charts":
        st.title("Charts")
        if st.session_state.chart_data:
            chart_type, data, x_axis, y_axis, axis_options = st.session_state.chart_data
            generate_chart(chart_type, data, x_axis, y_axis, axis_options)
        else:
            st.warning("No chart data available. Please generate a chart in the 'Category' page.")
