import streamlit as st
import pandas as pd
import datetime

# Streamlit app layout
st.write("""
    This app is designed to help you assign i7 and i5 indices to your samples in a 96-well format.
    The process involves selecting wells and generating matrices based on your selection. 
    i7 indices are assigned by column, and i5 indices are assigned by row.
""")
st.subheader("Well Selector")
st.write("Select two wells to define a range, and generate a matrix between those wells.")
st.write("Your selected data matrix is displayed in the sidebar. If you don't see the full matrix, adjust the sidebar's size or position for optimal viewing.")
st.write("If you mis-clicked, refresh the page to start over and select a new pair of wells.")

# Load the index data from the CSV file
index_df = pd.read_csv('index.csv')

# Create a sample dataframe for well structure (8 rows x 12 columns)
data = [[f'{chr(65 + row)}{col + 1}' for col in range(12)] for row in range(8)]
df = pd.DataFrame(data, columns=[f'A{i + 1}' for i in range(12)])

# Apply CSS styling for well selection buttons
st.markdown(
    """
    <style>
    /* Styling for well selection buttons */
    .stButton button {
        width: 60px;
        height: 40px;
        text-align: center;
        vertical-align: middle;
    }
        /* Increase the width of the sidebar */
    .css-1d391kg {
        width: 600px !important;  /* Adjust sidebar width as needed */
    }

    /* Adjust the matrix width inside the sidebar with small left margin */
    #matrix-container {
        max-width: 400px !important;  /* Adjust this value as needed for the matrix in sidebar */
        margin-left: 10px;  /* Set a small left margin */
        margin-right: auto;
    }

    /* Make the font smaller in the matrix to fit the sidebar */
    #matrix-container td, #matrix-container th {
        font-size: 22px !important;  /* Adjust the font size to make it smaller */
        padding: 5px;  /* Optional: Reduce padding to save space */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for user selections
if 'start_cell' not in st.session_state:
    st.session_state.start_cell = None
if 'end_cell' not in st.session_state:
    st.session_state.end_cell = None
if 'removal_wells' not in st.session_state:
    st.session_state.removal_wells = []

# Function to get the selection based on two cells
def get_selection(start_cell, end_cell):
    row_start = min(ord(start_cell[0]) - 65, ord(end_cell[0]) - 65)
    row_end = max(ord(start_cell[0]) - 65, ord(end_cell[0]) - 65)
    col_start = min(int(start_cell[1:]) - 1, int(end_cell[1:]) - 1)
    col_end = max(int(start_cell[1:]) - 1, int(end_cell[1:]) - 1)

    selection = []
    for r in range(row_start, row_end + 1):
        for c in range(col_start, col_end + 1):
            selection.append(df.iloc[r, c])
    return selection

# Matrix button selection for wells
for i in range(df.shape[0]):
    cols = st.columns(df.shape[1])
    for j in range(df.shape[1]):
        cell_value = df.iloc[i, j]
        with cols[j]:
            if st.button(cell_value, key=f'select_{cell_value}', use_container_width=True):
                if not st.session_state.start_cell:
                    st.session_state.start_cell = cell_value
                elif not st.session_state.end_cell:
                    st.session_state.end_cell = cell_value

# Define selected_data after selection logic
if st.session_state.start_cell and st.session_state.end_cell:
    selected_data = get_selection(st.session_state.start_cell, st.session_state.end_cell)
else:
    selected_data = []

# Remove Wells from Output (Multiple Selection)
st.subheader("Remove Wells from Output (Optional)")
st.write("Select wells to exclude from the output. To undo changes, simply refresh the page.")

for i in range(df.shape[0]):
    cols = st.columns(df.shape[1], gap="small")
    for j in range(df.shape[1]):
        cell_value = df.iloc[i, j]
        if cell_value not in st.session_state.removal_wells:
            if cols[j].button(cell_value, key=f"remove_{cell_value}", help=f"Remove {cell_value}"):
                st.session_state.removal_wells.append(cell_value)  # Add to removal list
        else:
            cols[j].markdown(f"""
                <div style="color: red; font-weight: bold; display: flex; justify-content: center; align-items: center; height: 100%; width: 100%; text-align: center;">
                    {cell_value}
                </div>
            """, unsafe_allow_html=True)
# In your sidebar, show only the final selected wells with formatting
with st.sidebar:
    st.title("Final Selected Data Matrix")
    final_matrix = df.copy()

    # Format for start and end cells, and handle removal and selection
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            cell_value = df.iloc[i, j]

            # Exclude the wells marked for removal from the display
            if cell_value in st.session_state.removal_wells:
                final_matrix.iloc[i, j] = ''  # Clear out removed wells
            # Highlight start and end cells
            elif cell_value == st.session_state.start_cell:
                final_matrix.iloc[i, j] = f'<span style="color:blue; font-weight:bold;">{cell_value}</span>'
            elif cell_value == st.session_state.end_cell:
                final_matrix.iloc[i, j] = f'<span style="color:red; font-weight:bold;">{cell_value}</span>'
            # Highlight selected wells
            elif cell_value in selected_data:
                final_matrix.iloc[i, j] = f'<span style="background-color:yellow; font-weight:bold; color:black;">{cell_value}</span>'
            else:
                final_matrix.iloc[i, j] = f'<span>{cell_value}</span>'

    # Render the final matrix with color and highlights applied
    st.markdown(f'<div id="matrix-container">{final_matrix.to_html(escape=False, index=False, header=False)}</div>', unsafe_allow_html=True)

# i7/i5 selection
st.subheader("Select i7 Column and i5 Row")
i7_col = st.selectbox("Select i7 Column", list(range(1, 13)))
i5_row = st.selectbox("Select i5 Row", list("ABCDEFGH"))

# Prefix input box
prefix = st.text_input("Enter a prefix for Sample_ID (optional)", value="")

# Generate horizontal output
output_data = []
for i in range(8):
    for j in range(12):
        well = df.iloc[i, j]
        if well in selected_data and well not in st.session_state.removal_wells:
            i5_value = f"{i5_row}{j + 1}"
            i5_data = index_df.loc[index_df['index'] == i5_value, ['i5-name', 'i5-index']].values[0]
            i7_value = f"{chr(65 + i)}{i7_col}"
            i7_data = index_df.loc[index_df['index'] == i7_value, ['i7-name', 'i7-index']].values[0]
            
            # Apply prefix
            sample_id = f"{prefix}{well}" if prefix else well
            
            output_data.append({"Sample_ID": sample_id, "Sample_name": "", "i7-name": i7_data[0], "i7-index": i7_data[1], "i5-name": i5_data[0], "i5-index": i5_data[1]})

# Generate vertical output
vertical_output_data = []
rows = [f"{chr(65 + r)}{c + 1}" for c in range(12) for r in range(8)]
for well in rows:
    if well in selected_data and well not in st.session_state.removal_wells:
        well_row = well[0]
        well_number = int(well[1:])
        i5_value = f"{i5_row}{well_number}"
        i5_row_data = index_df.loc[index_df['index'] == i5_value, ['i5-name', 'i5-index']].values[0]
        i7_value = f"{well_row}{i7_col}"
        i7_row_data = index_df.loc[index_df['index'] == i7_value, ['i7-name', 'i7-index']].values[0]
        
        # Apply prefix
        sample_id = f"{prefix}{well}" if prefix else well
        
        vertical_output_data.append({
            "Sample_ID": sample_id,
            "Sample_name": "",
            "i7-name": i7_row_data[0],
            "i7-index": i7_row_data[1],
            "i5-name": i5_row_data[0],
            "i5-index": i5_row_data[1]
        })

# Convert to DataFrame
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_df = pd.DataFrame(output_data)
vertical_output_df = pd.DataFrame(vertical_output_data)

# Download buttons
st.download_button("Download Horizontal Output as CSV", data=output_df.to_csv(index=False), file_name=f"horizontal_output_{timestamp}.csv", mime="text/csv")
st.write("### Horizontal Output →")
st.dataframe(output_df)

st.download_button("Download Vertical Output as CSV", data=vertical_output_df.to_csv(index=False), file_name=f"vertical_output_{timestamp}.csv", mime="text/csv")
st.write("### Vertical Output ↓")
st.dataframe(vertical_output_df)
