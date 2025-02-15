import streamlit as st 
import pandas as pd

# Load the index data from the CSV file
index_df = pd.read_csv('index.csv')

# Create a sample dataframe for well structure (8 rows x 12 columns)
data = [[f'{chr(65 + row)}{col + 1}' for col in range(12)] for row in range(8)]
df = pd.DataFrame(data, columns=[f'A{i + 1}' for i in range(12)])

# Initialize session state for selection
if 'start_cell' not in st.session_state:
    st.session_state.start_cell = None
if 'end_cell' not in st.session_state:
    st.session_state.end_cell = None
if 'removal_wells' not in st.session_state:
    st.session_state.removal_wells = []

# Function to get selected wells within the range
def get_selection(start_cell, end_cell):
    if not start_cell or not end_cell:
        return []

    # Convert well labels to indices
    start_row, start_col = ord(start_cell[0]) - 65, int(start_cell[1:]) - 1
    end_row, end_col = ord(end_cell[0]) - 65, int(end_cell[1:]) - 1

    # Ensure proper order regardless of selection order
    min_row, max_row = min(start_row, end_row), max(start_row, end_row)
    min_col, max_col = min(start_col, end_col), max(start_col, end_col)

    # Collect all wells within the range
    selection = [df.iloc[r, c] for r in range(min_row, max_row + 1) for c in range(min_col, max_col + 1)]
    return selection

# UI for selecting wells
st.title("Well Selector")
st.write("Select two wells to define a range.")

# Create button grid for selection
for i in range(df.shape[0]):
    cols = st.columns(df.shape[1])
    for j in range(df.shape[1]):
        cell_value = df.iloc[i, j]

        if cols[j].button(cell_value, key=cell_value):
            if not st.session_state.start_cell:
                st.session_state.start_cell = cell_value
            elif not st.session_state.end_cell:
                st.session_state.end_cell = cell_value

# Determine selected wells
selected_data = get_selection(st.session_state.start_cell, st.session_state.end_cell)

# Display selected range
if st.session_state.start_cell and st.session_state.end_cell:
    st.write(f"Selected range: {st.session_state.start_cell} to {st.session_state.end_cell}")
    st.write("Selected Wells:")
    st.write(", ".join(selected_data))

# Clear selection button
if st.button("Clear Selection"):
    st.session_state.start_cell = None
    st.session_state.end_cell = None
