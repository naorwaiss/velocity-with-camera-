import os
import pandas as pd

#this function run on the simulation computer or at the jetson
# i think i can combine it with the plot script


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

if __name__ == "__main__":
    convert_txt_to_excel()
