import os
import pandas as pd
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox

def get_contract(vehicle_identifier):
    return vehicle_contract_mapping.get(vehicle_identifier, "No Contract")

def process_file(file_path):
    df = pd.read_csv(file_path)

    # Add the Contract column to the dataframe
    df['Contract'] = df['Vehicle Identifier'].apply(get_contract)

    # Filter only completed trips
    completed_trips = df[df['Trip Status'] == 'completed']

    # Remove unnecessary columns
    completed_trips = completed_trips.drop(columns=['Rider ID Number', 'Rider Name'])

    # Replace '-' with NaN for the 'Enter Cash Collected (Driver Use Only)' column and convert to float
    completed_trips['Enter Cash Collected (Driver Use Only)'] = completed_trips['Enter Cash Collected (Driver Use Only)'].replace('-', None).astype(float)

    # Fill NaNs in 'Enter Cash Collected (Driver Use Only)' with 0 for summation purposes
    completed_trips['Enter Cash Collected (Driver Use Only)'].fillna(0, inplace=True)

    # Sum the 'Enter Cash Collected (Driver Use Only)' values for each 'Fleet Name', 'Contract', and 'Driver Name'
    cash_summary = completed_trips.groupby(['Fleet Name', 'Contract', 'Driver Name'])['Enter Cash Collected (Driver Use Only)'].sum().reset_index()
    cash_summary.columns = ['Fleet Name', 'Contract', 'Driver Name', 'cash']

    # Split the values in 'Pay On Vehicle (Driver Use Only)' column by commas
    completed_trips['Pay On Vehicle (Driver Use Only)'] = completed_trips['Pay On Vehicle (Driver Use Only)'].replace('-', None)
    completed_trips['Pay On Vehicle (Driver Use Only)'] = completed_trips['Pay On Vehicle (Driver Use Only)'].str.split(',')

    # Explode the payment types into separate rows
    completed_trips_exploded = completed_trips.explode('Pay On Vehicle (Driver Use Only)')

    # Filter out 'cash' from the exploded DataFrame
    completed_trips_exploded = completed_trips_exploded[completed_trips_exploded['Pay On Vehicle (Driver Use Only)'] != 'cash']

    # Count the occurrences of each payment type by 'Fleet Name', 'Contract', and 'Driver Name'
    payment_counts = completed_trips_exploded.groupby(['Fleet Name', 'Contract', 'Driver Name', 'Pay On Vehicle (Driver Use Only)']).size().unstack(fill_value=0)

    # Combining the cash summary with the payment counts
    final_result_completed = cash_summary.set_index(['Fleet Name', 'Contract', 'Driver Name']).join(payment_counts).reset_index()

    # Saving the final result to a CSV file
    csv_file_path = "Detailed_Payment_Summary_All_Fleets.csv"
    final_result_completed.to_csv(csv_file_path, index=False)

    # Directory to save the CSV files
    output_dir = "fleet_summary"
    os.makedirs(output_dir, exist_ok=True)

    for fleet_name, group_df in final_result_completed.groupby('Fleet Name'):
        # Saving the detailed drivers information for each fleet
        driver_file_name = f"{fleet_name.replace(' ', '_')}_Drivers.csv"
        driver_file_path = os.path.join(output_dir, driver_file_name)
        group_df.to_csv(driver_file_path, index=False)

    # # Create a ZIP file containing all the results
    # zip_file_path = "fleet_summaries.zip"
    # with zipfile.ZipFile(zip_file_path, 'w') as zipf:
    #     zipf.write(csv_file_path)
    #     for root, dirs, files in os.walk(output_dir):
    #         for file in files:
    #             zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))

    messagebox.showinfo("Process Completed", f"Results have been saved to fleet_summary")

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        process_file(file_path)

# Contracts data
contracts = {
    "AB Transit Inc.": ["449-2018B", "1022-2018", "1260-2018", "871-2022"],
    "Care Accessible Transportation": ["754-2022"],
    "Exact Care Inc.": ["106-2019", "8-2017"],
    "JD Taxi Inc.": ["657-2017"],
    "Mani-Handi Transit Ltd.": ["108-2019"],
    "Urban Transit Ltd.": ["449-2018A", "1259-2018", "107-2019"]
}

contract_vehicles = {
    "449-2018B": ["1201A BUS", "1202A BUS", "1203A BUS", "1204A BUS", "1205A BUS", "1206A BUS"],
    "1022-2018": ["721A CAR", "722A CAR", "723A CAR", "724A CAR", "725A CAR", "726A CAR", "TAOS1AB SUV"],
    "1260-2018": ["781A CAR", "782A CAR", "783A CAR", "784A CAR", "785A CAR", "786A CAR", "TAOS2AB SUV"],
    "871-2022": ["C7AB SUV", "C8AB SUV", "C9AB SUV", "C10AB SUV", "C11AB SUV", "C12AB SUV"],
    "754-2022": ["C1CA SUV", "C2CA SUV", "C3CA SUV", "C4CA SUV", "C5CA SUV", "C6CA SUV", "EXPL1CA"],
    "106-2019": ["801E BUS", "802E BUS", "803E BUS", "804E BUS", "805E BUS", "806E BUS"],
    "8-2017": ["1751E VAN", "1752E VAN", "1753E VAN", "1754E VAN", "1755E VAN", "1756E VAN"],
    "657-2017": ["657-01J CAR", "675-02J CAR", "675-03J CAR", "675-04J CAR", "675-05J CAR", "675-07J CAR"],
    "108-2019": ["201M CAR", "202M CAR", "203M CAR", "204M CAR", "205M CAR", "206M CAR", "207M CAR"],
    "449-2018A": ["1501U BUS", "1502U BUS", "1503U BUS", "1504U BUS", "1505U BUS", "1506U BUS"],
    "1259-2018": ["601U BUS", "602U BUS", "603U BUS", "604U BUS", "605U BUS", "606U BUS"],
    "107-2019": ["701U BUS", "702U BUS", "703U BUS", "704U BUS", "705U BUS", "706U BUS"]
}

# Reverse the mapping to get a vehicle to contract mapping
vehicle_contract_mapping = {vehicle: contract for contract, vehicles in contract_vehicles.items() for vehicle in vehicles}

# Create the main window
root = tk.Tk()
root.title("Fleet Data Processor")

# Create and place the file upload button
upload_button = tk.Button(root, text="Upload CSV File", command=select_file)
upload_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()
