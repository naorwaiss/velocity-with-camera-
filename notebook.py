import aiofiles
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Function to create a new notepad (file) with the specified content
async def create_notepad(file_path, content):
    async with aiofiles.open(file_path, 'w') as file:
        await file.write(content)

# Function to append content to an existing notepad (file)
async def append_to_notepad(file_path, content):
    async with aiofiles.open(file_path, 'a') as file:
        await file.write(content)

# Function to save velocity data to a notepad, either by creating a new notepad or appending to an existing one
async def save_velocity_data(file_path, velocity_data):
    # Format the velocity data to have 4 decimal places
    formatted_data = [format_number(V) for V in velocity_data]

    # Convert the list of velocity data to a string with newline separators
    table_string = '\n'.join(map(str, formatted_data)) + '\n'

    # If the file exists, append to it; otherwise, create a new notepad
    if os.path.exists(file_path):
        await append_to_notepad(file_path, table_string)
    else:
        await create_notepad(file_path, table_string)

# Function to save velocity data to a notepad (file) with a list of velocity values


# Function to format a number with 4 decimal places
def format_number(num):
    return "{:.4f}".format(num)



async def crate_notepad():
    notepad_path1 = 'delta_t.txt'
    notepad_path2= 'Vy.txt'
    notepad_path3 = 'Vx.txt'
    notepad_path4 = 'Vx_current.txt'
    notepad_path5 = 'Vy_current.txt' # i change here from vx to vy

    await create_notepad(notepad_path1, '')
    await create_notepad(notepad_path2, '')
    await create_notepad(notepad_path3, '')
    await create_notepad(notepad_path4, '')
    await create_notepad(notepad_path5, '')

async def save_to_note_pads(V, file_path):
    await save_velocity_data(file_path, [V])


def convert_txt_to_excel():
    # Get all .txt files in the current directory
    txt_files = [file for file in os.listdir() if file.endswith('.txt')]

    if not txt_files:
        print("No text files found in the directory.")
        return

    # Create a Pandas DataFrame to hold the data
    df = pd.DataFrame()

    # Read each text file and append its content to the DataFrame
    for txt_file in txt_files:
        file_path = os.path.join(os.getcwd(), txt_file)
        data = pd.read_csv(file_path, delimiter='\t')  # Assuming tab-separated values, adjust if needed
        df = pd.concat([df, data], axis=1)

    # Add column labels
    column_labels = [os.path.splitext(file)[0] for file in txt_files]
    df.columns = column_labels

    # Write the DataFrame to an Excel file
    excel_file_path = 'combined_data_with_labels.xlsx'
    df.to_excel(excel_file_path, index=False)

    print(f"Data has been combined and saved to {excel_file_path}")

def plot(save_path=None):
    file_path = '/home/naor/fhsbs/velocity-with-camera-/combined_data_with_labels.xlsx'
    table_data = pd.read_excel(file_path)

    # Print the original DataFrame
    print("Original DataFrame:")
    print(table_data)

    # Check if 'delta_t' column exists and there are rows in the DataFrame
    if 'delta_t' not in table_data.columns or table_data.empty:
        print("Error: Missing 'delta_t' column or empty DataFrame.")
        return

    # Print the DataFrame after finding NaN rows
    print("DataFrame after finding NaN rows:")
    print(table_data)

    # Check for NaN values in the DataFrame
    print("NaN values in the DataFrame:")
    print(table_data.isna().sum())

    # Handle NaN values (example: filling NaN values with 0)
    table_data = table_data.fillna(0)

    # Print the DataFrame after filling NaN values
    print("DataFrame after filling NaN values:")
    print(table_data)

    # Find the first occurrence of NaN in any column
    nan_row = table_data.isna().any(axis=1).idxmax()

    # Print the DataFrame after removing NaN rows
    print("DataFrame after removing NaN rows:")
    print(table_data)

    # Check if there are rows in the modified DataFrame
    if table_data.empty:
        print("Error: Empty DataFrame after removing NaN rows.")
        return

    # Determine the time step from the first column
    delta_t = table_data.loc[0, 'delta_t']

    # Create a new column for time
    time_column = np.arange(0, len(table_data) * delta_t, delta_t)
    table_data['Time'] = time_column

    # Display the modified table
    print("DataFrame after adding 'Time' column:")
    print(table_data)

    # Extract data for plotting (replace with actual variable names)
    V_x = table_data['Vx']
    V_x_current = table_data['Vx_current']
    V_y = table_data['Vy']
    V_y_current = table_data['Vy_current']

    # Print data arrays before plotting
    print("Time Column:")
    print(time_column)
    print("V_x:")
    print(V_x)
    print("V_x_current:")
    print(V_x_current)
    print("V_y:")
    print(V_y)
    print("V_y_current:")
    print(V_y_current)

    # Plot V (x and x current) in function of t
    plt.figure()
    plt.plot(time_column, V_x, linewidth=2, label='V_x')
    plt.plot(time_column, V_x_current, linewidth=2, label='V_x_current')
    plt.xlabel('Time')
    plt.ylabel('V (x)')
    plt.title('V (x and x current) in function of time')
    plt.legend()
    plt.grid()

    if save_path:
        save_directory = os.path.join(save_path, 'plots')
        os.makedirs(save_directory, exist_ok=True)
        plt.savefig(os.path.join(save_directory, 'V_x_plot.png'))
    else:
        plt.show()

    # Plot V (y and y current) in function of t
    plt.figure()
    plt.plot(time_column, V_y, linewidth=2, label='V_y')
    plt.plot(time_column, V_y_current, linewidth=2, label='V_y_current')
    plt.xlabel('Time')
    plt.ylabel('V (y)')
    plt.title('V (y and y current) in function of time')
    plt.legend()
    plt.grid()

    if save_path:
        plt.savefig(os.path.join(save_directory, 'V_y_plot.png'))
    else:
        plt.show()

# Example usage with saving the plots in '/home/naor/fhsbs/velocity-with-camera-/plots/'

def notebook():
    # this function gave us the graph
    convert_txt_to_excel()
    plot(save_path='/home/naor/fhsbs/velocity-with-camera-/')

if __name__ == "__main__":
    notebook()


def notebook():
    # this function gave us the graph
    convert_txt_to_excel()
    plot(save_path='/home/naor/fhsbs/velocity-with-camera-/')

if __name__ == "__main__":
    notebook()
