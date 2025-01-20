from sklearn.linear_model import SGDRegressor
from river.metrics import MSE
from river.compat.sklearn_to_river import convert_sklearn_to_river
from helper.kafka_utils import create_kafka_consumer, consume_messages_from_kafka, create_kafka_producer, send_message_to_kafka
import joblib
from river import preprocessing
import pandas as pd
from config.config import SELECTED_FEATURES

PREDICTIONS_TOPIC = 'prediction-output'
producer_preds = create_kafka_producer()

# Model sklearn trained
sklearn_scaler = joblib.load("models/batch_standard_scaler.joblib")
sklearn_model = joblib.load("models/batch_model_SGD.joblib")

# Online model from scratch
model_cold_start = convert_sklearn_to_river(SGDRegressor())
river_scaler = preprocessing.StandardScaler()

# Online model from sklearn trained model
model_pre_trained = convert_sklearn_to_river(sklearn_model)

# Metrics for each of the model
metric_sklearn = {'n': 0, 'mse': 0}
metric_cold_start = MSE()
metric_pre_trained = MSE()

def train_and_predict():
    """
    Consume messages from Kafka, train the model incrementally, and send predictions.
    """
    consumer = create_kafka_consumer('weather-live-data-2', 'live-data-group')
    previous_timestamp, scaled_prev_features = None, None
    previous_pred_pre_trained, previous_pred_cold_start, previous_pred_sklearn = None, None, None

    for message in consume_messages_from_kafka(consumer):
        timestamp, features, target = message["last_updated"], message["processed_sample"], message["target"]

        # Prepare and predict for current sample

        features["prev_target"] = target

        river_scaler.learn_one(features)
        scaled_features = river_scaler.transform_one(features)

        y_pred_pre_trained = model_pre_trained.predict_one(scaled_features)
        y_pred_cold_start = model_cold_start.predict_one(scaled_features)

        feature_values = list(features.values())
        feature_df = pd.DataFrame([feature_values], columns=SELECTED_FEATURES)
        scaled_features_sklearn = sklearn_scaler.transform(feature_df)
        y_pred_sklearn = sklearn_model.predict(scaled_features_sklearn)[0]


        # Evaluate prediction for sample from previous hour
        if (previous_timestamp is not None) and (timestamp - previous_timestamp == 3600):

            # online models
            metric_pre_trained.update(target, previous_pred_pre_trained)
            model_pre_trained.learn_one(scaled_prev_features, target)

            metric_cold_start.update(target, previous_pred_cold_start)
            model_cold_start.learn_one(scaled_prev_features, target)

            # sklearn model
            error_sklearn = (target - previous_pred_sklearn) ** 2
            metric_sklearn['mse'] = ((metric_sklearn['n'] * metric_sklearn['mse']) + error_sklearn) / (metric_sklearn['n'] + 1)
            metric_sklearn['n'] += 1

            send_message_to_kafka(producer_preds, PREDICTIONS_TOPIC, {
                'timestamp': timestamp,
                'prediction pre trained': max(0, previous_pred_pre_trained),
                'prediction cold start': max(0, previous_pred_cold_start),
                'prediction sklearn': max(0, previous_pred_sklearn),
                'MSE cold start': metric_cold_start.get(),
                'MSE pre trained': metric_pre_trained.get(),
                'MSE sklearn': metric_sklearn['mse'],
                'actual': target,
                'next prediction': max(0, y_pred_pre_trained)
            })
        
        previous_timestamp, scaled_prev_features = timestamp, scaled_features
        previous_pred_pre_trained, previous_pred_cold_start = y_pred_pre_trained, y_pred_cold_start
        previous_pred_sklearn = y_pred_sklearn