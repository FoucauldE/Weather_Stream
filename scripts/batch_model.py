import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from river.compat.sklearn_to_river import convert_sklearn_to_river
import matplotlib.pyplot as plt
import seaborn as sns
from config.config import VARIABLES_TO_KEEP

csv_name = "Data/final_2025-01-08_00-00-00_2025-01-15_00-00-00_past_data_with_Y.csv"

# Load the data
data = pd.read_csv(csv_name)
data = data.rename(columns={"target": "precip_mm"})
data = data.rename(columns={"wind_degree_cos": "wind_degree"})

# Define X and y
X = data[VARIABLES_TO_KEEP]  # Features
y = data["futur_target"]  # Target

# 3. Séparation des données
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=56)

# Pipeline
scaler = StandardScaler()
model = SGDRegressor()

# Entraînement de la pipeline linear
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
model.fit(X_train, y_train)

# 4. Évaluation
y_pred = model.predict(X_test)
print("Train MSE: ", mean_squared_error(y_train, model.predict(X_train)))
print("Test MSE: ", mean_squared_error(y_test, model.predict(X_test)))

print("Train R²: ", r2_score(y_train, model.predict(X_train)))
print("Test R²: ", r2_score(y_test, model.predict(X_test)))

# 5. Sauvegarde de la pipeline
joblib.dump(scaler, f"Models/batch_standard_scaler.joblib")
joblib.dump(model, f"Models/batch_model_SGD.joblib")

# 6. Conversion de la pipeline en river
river_model = convert_sklearn_to_river(model)
print("Model converted to River!")

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
            plt.savefig("Graphs/correlation_matrix.png")
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
            plt.savefig("Graphs/correlation_futur_target.png")
        plt.show()

if __name__ == "__main__":

    print("Training the batch model on past data...")
    features_selection()