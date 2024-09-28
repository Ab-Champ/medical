import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\abhis\Downloads\diseases_2.xls")
    df.drop('Unnamed: 0', axis=1, inplace=True)
    return df


df = load_data()

# Define the medicines and search columns
Medicines = ['name', 'substitute0', 'substitute1', 'substitute2', 'substitute3', 'substitute4']
search_columns = Medicines + ['Therapeutic Class', 'Use_cases']

def get_corresponding_values(df, word, search_columns):
    word = word.lower()

    # Filter rows based on whether the search term appears in any of the search columns
    mask = pd.Series(False, index=df.index)

    # Use vectorized string matching for faster search
    for col in search_columns:
        if col in df.columns and df[col].dtype == 'object':  # Check only string columns
            mask |= df[col].str.lower().str.contains(word, na=False)

    # Return the filtered DataFrame where the mask is True
    return df[mask]

# Streamlit app layout
st.title('Drug and Use Case Search')

# Create a form for the input
with st.form(key='search_form'):
    word = st.text_input('Enter the Medicine, Use Case, or Therapeutic Class to search:')
    submit_button = st.form_submit_button(label='Search')

# Initialize session state to hold search results and selected letter
if 'results' not in st.session_state:
    st.session_state.results = None
    st.session_state.selected_letter = None

# Search logic
if submit_button:
    if word:
        # Show a loading message while searching
        with st.spinner('Searching...'):
            # Perform the search
            st.session_state.results = get_corresponding_values(df, word, search_columns)
            st.session_state.selected_letter = None  # Reset the selected letter

# Check if results exist
if st.session_state.results is not None and not st.session_state.results.empty:
    # Display unique starting letters only if there are multiple results
    if len(st.session_state.results) > 1:
        # Get unique starting letters
        unique_letters = sorted(set(st.session_state.results['name'].str[0].str.upper()))

        # Create a collapsible section for selecting letters
        with st.sidebar.expander("Filter by Starting Letter", expanded=False):
            for letter in unique_letters:
                if st.button(letter, key=letter):  # Use a unique key for each button
                    st.session_state.selected_letter = letter  # Store the selected letter

    # Filter by selected letter if applicable
    if st.session_state.selected_letter:
        filtered_results = st.session_state.results[st.session_state.results['name'].str.startswith(st.session_state.selected_letter.lower())]
    else:
        filtered_results = st.session_state.results

    # Check if there are any filtered results
    if filtered_results.empty:
        st.write("No results found for the selected letter.")
    else:
        # Pagination logic
        page_size = 15
        total_results = len(filtered_results)
        total_pages = (total_results // page_size) + (total_results % page_size > 0)  # Calculate total pages

        if total_pages > 0:
            # Select page number only if there are results
            page_number = st.selectbox('Select page:', range(1, total_pages + 1), index=0)

            # Calculate the start and end indices for slicing
            start_idx = (page_number - 1) * page_size
            end_idx = min(start_idx + page_size, total_results)  # Ensure the end index does not exceed total results
            paginated_result = filtered_results.iloc[start_idx:end_idx]

            # If results are found, display them
            st.write("Search Results:")
            displayed_medicines = set()  # To track medicines already displayed to avoid duplicates
            
            for index, row in paginated_result.iterrows():
                # Default is to use the main medicine name
                medicine_name = row['name']  
                matched_substitute = None

                # Check if the search term matches any of the substitute columns
                for substitute in ['substitute0', 'substitute1', 'substitute2', 'substitute3', 'substitute4']:
                    if isinstance(row[substitute], str) and word in row[substitute].lower():
                        matched_substitute = row[substitute]
                        # Swap substitute name with the main medicine name
                        medicine_name = matched_substitute
                        break

                # Check if the result has already been displayed
                if medicine_name not in displayed_medicines:
                    displayed_medicines.add(medicine_name)  # Add it to the set of displayed medicines

                    # Display the result
                    st.markdown(f"<h1 style='font-size:36px;'>{medicine_name}</h1>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style='line-height: 1.8;'>
                        <h3 style='font-size:24px;'><strong>Therapeutic Class:</strong> {row['Therapeutic Class']}</h3>
                        <strong>Chemical Class:</strong> {row['Chemical Class']}<br>
                        <strong>Action Class:</strong> {row['Action Class']}<br>
                        <strong>Habit Forming:</strong> {row['Habit Forming']}<br>
                        <strong>Use Cases:</strong> {row['Use_cases']}<br>
                        <strong>Side Effects:</strong> {row['Side_Effects']}<br><br>
                        <h4 style='font-size:20px;'><strong>Substitutes:</strong></h4>
                        - {row['substitute0']}<br>
                        - {row['substitute1']}<br>
                        - {row['substitute2']}<br>
                        - {row['substitute3']}<br>
                        - {row['substitute4']}<br>
                    </div>
                    """, unsafe_allow_html=True)

                    # If a substitute was matched, mention that the name was swapped
                    if matched_substitute:
                        st.markdown(f"<p><em>Note: '{matched_substitute}' was matched as a substitute.</em></p>", unsafe_allow_html=True)
else:
    st.write("Please enter a word to search.")