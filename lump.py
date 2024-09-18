import pandas as pd
import streamlit as st

# Step 1: Simulate the ending values for a one-time lump sum investment
def simulate_lump_sum_ending_value(df_column, initial_investment, num_years, row_increment):
    results = []
    for start_row in range(0, len(df_column) - (row_increment * (num_years - 1))):
        investment_value = initial_investment  # Initial lump sum investment
        for year in range(num_years):
            current_row = start_row + (row_increment * year)
            factor = df_column[current_row]
            investment_value *= factor  # Compounding the investment
        results.append(investment_value)
    return results

# Step 2: Calculate the required initial investment based on the ending value index
def calculate_required_lump_sum_investment(ending_values, goal, confidence_level):
    sorted_values = sorted(ending_values)
    index = int((1 - confidence_level) * len(sorted_values))  # Find the index for the confidence level
    ending_value_at_confidence = sorted_values[index]
    required_initial_investment = goal / ending_value_at_confidence
    return required_initial_investment

# Load the Excel file with historical return factors
file_path = 'all_portfolio_annual_factor_20_bps.xlsx'
sheet_name = 'allocation_factors'
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Streamlit interface for selecting parameters
st.title("Lump Sum Investment Calculator")
st.write("Select parameters to calculate the required lump sum investment:")

# Streamlit sliders for interactive input
goal = st.slider("Goal ($)", min_value=10000, max_value=3000000, value=100000, step=10000)
num_years = st.slider("Number of Years", min_value=1, max_value=41, value=30)
confidence_level = st.slider("Confidence Level (%)", min_value=50, max_value=100, value=90) / 100
row_increment = 12  # Assuming monthly data, skip 12 rows for annual factors

# Display initial message to ensure the page is not blank
st.write("Press the 'Calculate' button to see the required lump sum investment.")

# Button to trigger calculation
if st.button("Calculate"):
    # Loop through each allocation and calculate the required initial investment
    results_summary = []
    for column_name in df.columns:
        if pd.api.types.is_numeric_dtype(df[column_name]):
            # Step 1: Simulate the ending value for a lump sum investment for this allocation
            df_column = df[column_name]
            ending_values = simulate_lump_sum_ending_value(df_column, 1, num_years, row_increment)  # Use $1 as the initial investment
            
            # Step 2: Calculate the required initial lump sum investment based on the ending values
            required_initial_investment = calculate_required_lump_sum_investment(ending_values, goal, confidence_level)
            
            # Store the results for this allocation, adding number of years and goal
            results_summary.append({
                'Allocation': column_name,
                'Number of Years': num_years,
                'Goal': goal,
                'Required Initial Investment': int(required_initial_investment)  # Convert to integer for no decimals
            })
    
    # Convert results to a DataFrame for easy viewing
    results_df = pd.DataFrame(results_summary)
    
    # Display the DataFrame in Streamlit
    st.write("Results:")
    st.write(results_df)

    # Option to download the DataFrame as an Excel file
    output_file = 'required_initial_investment_by_allocation.xlsx'
    results_df.to_excel(output_file, index=False)
    st.write(f"Required initial investments for all allocations have been saved to {output_file}.")

    # Download button for CSV version
    st.download_button(
        label="Download Results as CSV",
        data=results_df.to_csv(index=False),
        file_name='required_initial_investment_by_allocation.csv',
        mime='text/csv'
    )