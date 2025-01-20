# Cloud Cover Monitoring and Forecasting

This repository provides a real-time monitoring system for Rainfall in order to compare performance between different ML models, especially between static and online approches. It uses data from the [Weather API](https://www.weatherapi.com/) and can be easily used through a Streamlit interface.

## Steps to Get Started

First clone the repository and insert [your private API key](https://www.weatherapi.com/signup.aspx) in the `config/private_config.py` file, following the template `config/template_private_config.py`.

Install all necessary dependencies by running:
```bash
   pip install -r requirements.txt
```

To start Zookeeper and Kafka, Windows users can run `./run_kafka.sh` from a bash script (assuming Kafka can be found in `C:/kafka/`).

Else, you can also start Zookeeper and Kafka by running
```bash
   # On Linux
   bin/zookeeper-server-start.sh config/zookeeper.properties
   bin/kafka-server-start.sh config/server.properties

   # On Windows
   .\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
   .\bin\windows\kafka-server-start.bat .\config\server.properties
```

After starting Zookeeper and Kafka, you can start running our streamlit app by running
```bash
   python -m streamlit run .\app\Home.py
```

Note: Windows users might need to set the Python Path
```bash
   $env:PYTHONPATH="<your_project_path>"
```

## Usage

Once you launched the streamlit app, feel free to discover our features to help you predict rainfall in the coming hour:
**What you can do:**
1. **⛅ Consult weather**: View real-time weather insights for any location on the globe. 🌍
2. **⚙️ Train a static model**: Download past data and train/test your own static model to predict the rain. 🌧️
3. **🔮 Access Predictions**: Explore forecasts for rainfall in the coming hour and compare the results with other models. 🔋