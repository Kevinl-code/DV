import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_option_menu import option_menu

# Sidebar using option_menu
def sidebar():
    selected = option_menu(
        menu_title="Main Menu",
        options=["Import Data", "Category"],
        icons=["upload", "book"],
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
        # Read Excel file
        data = pd.read_excel(file)

        # Connect to SQLite database
        conn = sqlite3.connect("kevinw.db")
        cursor = conn.cursor()

        # Drop table if exists to replace data
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

        # Save DataFrame to SQLite
        data.to_sql(table_name, conn, index=False, if_exists="replace")

        conn.commit()
        conn.close()
        return "Data uploaded successfully!"
    except Exception as e:
        return f"Error: {e}"

# Main application logic
if 'page' not in st.session_state:
    st.session_state.page = "front_page"

if st.session_state.page == "front_page":
    front_page()
else:
    # Sidebar appears on the left
    with st.sidebar:
        selected_page = sidebar()

    # Handle selected page
    if selected_page == "Import Data":
        st.title("Import Data")
        # File uploader
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
        table_name = st.text_input("Enter table name", placeholder="data_table")

        if uploaded_file is not None and table_name:
            st.write("File Uploaded:")
            st.write(uploaded_file.name)

            if st.button("Upload to Database"):
                result = upload_to_db(uploaded_file, table_name)
                st.success(result)

    elif selected_page == "Category":
        st.title("Category")
        # Connect to SQLite and get available tables
        conn = sqlite3.connect("kevinw.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Convert list of tuples to a list of table names
        table_names = [table[0] for table in tables]

        if table_names:
            # Dropdown for selecting a table
            selected_table = st.selectbox("Choose a category (table)", options=table_names)

            if selected_table:
                # Fetch data from the selected table
                data = pd.read_sql(f"SELECT * FROM {selected_table}", conn)

                # Get unique years from the 'year' column
                if 'year' in data.columns:
                    years = data['year'].dropna().unique().tolist()
                    years.sort()
                    years.insert(0, "All years")

                    # Year selection
                    year_selection = st.selectbox("Select year", years)

                    # Multicheck widget, enabled only for specific year selection
                    columns = [col for col in data.columns if col != 'year']

                    if year_selection == "All years":
                        selected_columns = []  # Disable multi-select for "All years"
                    else:
                        selected_columns = st.multiselect("Select columns", columns, default=columns)

                    st.markdown("**Select X-axis**")
                    x_axis = "Year"
                    st.text(x_axis)  # Displaying "Year" as the only option

                    st.markdown("**Select Y-axis**")
                    y_axis = st.selectbox("", options=columns)

                    if st.button("Generate Chart"):
                        filtered_df = data

                        # Filter data based on year selection
                        if year_selection != "All years":
                            filtered_df = data[data['year'] == year_selection]

                        if selected_columns:
                            filtered_df = filtered_df[selected_columns]

                        # Generate chart dynamically based on selections
                        chart_type = st.selectbox(
                            "Select Chart Type",
                            options=["Pie Chart", "Line Chart", "Bar Chart", "Column Chart"]
                        )

                        if x_axis and y_axis:
                            if chart_type == "Pie Chart":
                                fig = px.pie(filtered_df, names=x_axis, values=y_axis, title="Pie Chart")
                                st.plotly_chart(fig)
                            elif chart_type == "Line Chart":
                                fig = px.line(filtered_df, x=x_axis, y=y_axis, title="Line Chart")
                                st.plotly_chart(fig)
                            elif chart_type == "Bar Chart":
                                fig = px.bar(filtered_df, x=x_axis, y=y_axis, title="Bar Chart")
                                st.plotly_chart(fig)
                            elif chart_type == "Column Chart":
                                fig = px.bar(filtered_df, x=x_axis, y=y_axis, title="Column Chart", orientation='h')
                                st.plotly_chart(fig)

        conn.close()


