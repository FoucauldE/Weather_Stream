import pandas as pd
from sklearn.model_selection import train_test_split
import os

def format_csv(csv_path="Data/all_weather_data.csv", prediction_distance=1):
    """
    Input: csv file
    Output: the same but with the target added at the end of each line
    """
    # Load the csv file
    df = pd.read_csv(csv_path)

    # Add the last column of the next row to the current row
    df['y_target'] = df['precip_mm'].shift(-1)
    df = df.iloc[:-1]

    # Save to a new CSV file
    file_path = csv_path
    base_directory = os.path.dirname(csv_path)
    output_file_path = os.path.join(base_directory, 'all_weather_data_with_Y.csv')
    df.to_csv(output_file_path, index=False)

def train_test_csv(file_path):
    # Get the file
    file_path = file_path
    data = pd.read_csv(file_path)
    base_directory = os.path.dirname(file_path)
    # Split into train and test
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)
    # Output file paths
    train_file_path = os.path.join(base_directory, 'train_data_historical.csv')
    test_file_path = os.path.join(base_directory, 'test_data_historical.csv')
    # Save the outputs
    train_data.to_csv(train_file_path, index=False)
    test_data.to_csv(test_file_path, index=False)