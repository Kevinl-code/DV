import streamlit as st
import subprocess
import os
import matplotlib.pyplot as plt
import zipfile

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Charts", "Export"])

# Charts Page
if page == "Charts":
    st.title("Charts Page")

    # Example chart (you can add more charts here)
    data = {
        'data1': [1, 2, 3, 4],
        'data2': [10, 20, 30, 40]
    }

    fig, ax = plt.subplots()
    ax.plot(data['data1'], label='Data 1')
    ax.plot(data['data2'], label='Data 2')
    ax.set_title("Example Line Chart")
    ax.legend()

    # Display the chart
    st.pyplot(fig)

    # Export button
    if st.button("Export"):
        st.success("Export button clicked! Proceed to the Export page to choose export options.")

# Export Page
elif page == "Export":
    st.title("Export Page")

    # Dropdown to choose export type
    export_type = st.selectbox(
        "Choose export type:",
        ("PDF", "ZIP", "Image")
    )
    st.write(f"Selected export type: {export_type}")

    # Input for file name
    file_name = st.text_input("Enter file name (without extension):", value="exported_chart")

    # Button to open file dialog for directory selection
    if st.button("Browse File Location"):
        # Call the external script to open file dialog
        result = subprocess.run(['python', 'file_dialog.py'], capture_output=True, text=True)
        file_location = result.stdout.strip()  # Extract the directory path from the script
        if file_location:
            st.write(f"Selected directory: {file_location}")
        else:
            st.error("No directory selected. Please try again.")

    if st.button("Save Export"):
        # Validate file location
        if file_location and os.path.isdir(file_location):
            # Prepare the chart for export
            if export_type == "PDF":
                # Save as PDF
                pdf_path = os.path.join(file_location, f"{file_name}.pdf")
                fig.savefig(pdf_path, format="pdf")
                st.success(f"Chart saved as PDF at {pdf_path}")
            
            elif export_type == "ZIP":
                # Save as ZIP (contains the image file)
                zip_path = os.path.join(file_location, f"{file_name}.zip")
                image_path = os.path.join(file_location, f"{file_name}.png")
                
                # Save the image temporarily
                fig.savefig(image_path, format="png")

                # Create a zip file containing the chart image
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    zipf.write(image_path, os.path.basename(image_path))

                # Clean up the temporary image file
                os.remove(image_path)
                st.success(f"Chart saved as ZIP at {zip_path}")
            
            elif export_type == "Image":
                # Save as PNG image
                image_path = os.path.join(file_location, f"{file_name}.png")
                fig.savefig(image_path, format="png")
                st.success(f"Chart saved as image at {image_path}")
        else:
            st.error("Invalid directory. Please select a valid directory.")
