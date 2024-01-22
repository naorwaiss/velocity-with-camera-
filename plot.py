import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



file_path = 'C:/Users/naorw/proj/combined_data_with_labels.xlsx'
table_data = pd.read_excel(file_path)

# Find the first occurrence of NaN in any column
nan_row = table_data.isna().any(axis=1).idxmax()

# Remove rows from the NaN occurrence to the end
if not pd.isna(nan_row):
    table_data = table_data.loc[:nan_row - 1, :]

# Determine the time step from the first column
delta_t = table_data.loc[0, 'delta_t']

# Create a new column for time
time_column = np.arange(0, len(table_data) * delta_t, delta_t)
table_data['Time'] = time_column

# Display the modified table
print(table_data)

# Extract data for plotting (replace with actual variable names)
V_x = table_data['Vx']
V_x_current = table_data['Vx_current']
V_y = table_data['Vy']
V_y_current = table_data['Vy_current']

# Plot V (x and x current) in function of t
plt.figure()
plt.plot(time_column, V_x, linewidth=2, label='V_x')
plt.plot(time_column, V_x_current, linewidth=2, label='V_x_current')
plt.xlabel('Time')
plt.ylabel('V (x)')
plt.title('V (x and x current) in function of time')
plt.legend()
plt.grid()
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
plt.show()
