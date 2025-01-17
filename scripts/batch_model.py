import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from river.compat.sklearn_to_river import convert_sklearn_to_river
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import seaborn as sns
from config.config import SELECTED_FEATURES


def load_and_prepare_csv(csv_name):
    # Load the data
    data = pd.read_csv(csv_name)
    data = data.rename(columns={"target": "prev_target"})
    return data


def plot_precip_evolution(data, save=True):
    # In order to plot precip_mm evolution in time
    if "last_updated" in data.columns:
        data["date"] = pd.to_datetime(data["last_updated"], unit="s").dt.strftime("%Y-%m-%d %H-%m-%s")
        data = data.sort_values("last_updated")

    # Plot
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=data,
        x=data.index if "date" not in data.columns else "date",
        y="prev_target",
        marker="o",
        color="blue",
    )
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=10))
    plt.xticks(rotation=45)
    #plt.locator_params(axis='x', nbins=15)
    plt.title("Evolution of precip_mm", fontsize=16)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("precipitation (mm)", fontsize=12)
    plt.grid(visible=True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    if save:
        output_dir = "Graphs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, "evolution_of_precip_mm.png")
        plt.savefig(output_path)
    plt.show()


def temporal_train_test_split(data, split_coef=0.8, verbose=False):
    """
    This function aims to split according to the temporal order not to have data leakage.
    Also, it ensures every city is represented in the same proportion in train and test sets.
    """
    ### Split the data
    data["lat_lon"] = data[["lat", "lon"]].apply(lambda row: f"{row['lat']}_{row['lon']}", axis=1)
    unique_lat_lon = data["lat_lon"].unique()  # List of unique couple (1 couple = 1 city)
    #data.to_csv("with_lat_lon_column.csv", index=False)

    # Prepare the outputs
    X_train_list, X_test_list = [], []
    y_train_list, y_test_list = [], []

    for lat_lon in unique_lat_lon:
        # Filter by couple (lat, lon)
        city_data = data[data["lat_lon"] == lat_lon]

        # Compute the split index
        split_idx = int(len(city_data) * split_coef)
        
        # Split in the temportal ordrer for the city considered
        X_city_train = city_data.iloc[:split_idx][SELECTED_FEATURES]
        y_city_train = city_data.iloc[:split_idx]["futur_target"]
        X_city_test = city_data.iloc[split_idx:][SELECTED_FEATURES]
        y_city_test = city_data.iloc[split_idx:]["futur_target"]

        # Add to the outputs
        X_train_list.append(X_city_train)
        X_test_list.append(X_city_test)
        y_train_list.append(y_city_train)
        y_test_list.append(y_city_test)

    # Concatenate
    X_train = pd.concat(X_train_list, axis=0)
    X_test = pd.concat(X_test_list, axis=0)
    y_train = pd.concat(y_train_list, axis=0)
    y_test = pd.concat(y_test_list, axis=0)

    if verbose:
        # Check sizes
        print("Train set size:", X_train.shape, y_train.shape)
        print("Test set size:", X_test.shape, y_test.shape)

    return X_train, X_test, y_train, y_test


def pipeline_fit_save(X_train, X_test, y_train, y_test, save=True, model=SGDRegressor()):
    """
    This function fit the data with the train set, save the pipeline trained and print some scores.
    """
    # Pipeline
    scaler = StandardScaler()
    model = model

    # Train the pipeline
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    model.fit(X_train, y_train)

    # Evaluate the model
    print("Train MSE: ", mean_squared_error(y_train, model.predict(X_train)))
    print("Test MSE: ", mean_squared_error(y_test, model.predict(X_test)))

    print("Train R²: ", r2_score(y_train, model.predict(X_train)))
    print("Test R²: ", r2_score(y_test, model.predict(X_test)))

    if save:
        # Save the pipeline
        joblib.dump(scaler, f"Models/batch_standard_scaler.joblib")
        joblib.dump(model, f"Models/batch_model_SGD.joblib")

    # Test the conversion into to rive
    try:
        river_model = convert_sklearn_to_river(model)
        print("Model can be converted to River!")
    except ValueError as e:
        print(f"Error: The model is not convertible to River. Details: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during conversion. Details: {e}")

def features_selection(correl_matrix_plot=True, correl_with_target=True, save=True):
    csv_name = "Data/final_2025-01-08_00-00-00_2025-01-15_00-00-00_past_data_with_Y.csv"

    # Load the data
    data = pd.read_csv(csv_name)
    data = data.rename(columns={"target": "precip_mm"})

    # Compute the correlation matrix
    correlation_matrix = data.corr()

    if correl_matrix_plot:
        # Plot it
        plt.figure(figsize=(12, 8))
        sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, linewidths=0.5)
        plt.title("Correlation matrix", fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        if save:
            output_dir = "Graphs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, "correlation_matrix.png")
            plt.savefig(output_path)
        plt.show()

    if correl_with_target:
        # Absolute correlation with the target computation
        target_corr = correlation_matrix["futur_target"].apply(abs).sort_values(ascending=False)
        # Plot the results
        plt.figure(figsize=(12, 8))
        sns.barplot(
            x=target_corr.index,
            y=target_corr.values,
            hue=target_corr.index,
            palette="coolwarm",
            legend=False
        )
        plt.title("Absolute correlation of the features with the target", fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.ylabel("Absolute correlation", fontsize=14)
        plt.tight_layout()
        if save:
            output_dir = "Graphs"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_path = os.path.join(output_dir, "correlation_futur_target.png")
            plt.savefig(output_path)
        plt.show()

if __name__ == "__main__":

    print("Training the batch model on past data...")
    # Define the file name
    csv_name = 'Data/DEFINITIVE_2025-01-10_00-00-00_2025-01-17_00-00-00_past_data_with_Y.csv'
    #Load the data
    data = load_and_prepare_csv(csv_name)
    # Plot the evolution of the target
    plot_precip_evolution(data, save=True)
    # Plot graphs for feature selection
    features_selection(save=True)
    # Temporal train/test split
    X_train, X_test, y_train, y_test = temporal_train_test_split(data, verbose=True, split_coef=0.8)
    # Define the pipeline, fit and print several scores
    pipeline_fit_save(X_train, X_test, y_train, y_test, save=True, model=SGDRegressor())