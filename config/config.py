API_URL = 'http://api.weatherapi.com/v1'
KAFKA_BROKER = 'localhost:9092'
# ARCHIVE_DIR = './archives'
# WAIT_TIME = 10

VARIABLES_TO_KEEP = ["lat",
                    "lon",
                    "time_epoch",
                    "temp_c",
                    "is_day",
                    "wind_kph",
                    "wind_sin",
                    "wind_cos",
                    "pressure_mb",
                    "humidity",
                    "cloud",
                    "feelslike_c",
                    "windchill_c",
                    "heatindex_c",
                    "dewpoint_c",
                    "vis_km",
                    "gust_kph",
                    "uv"                  
]

TARGET_VARIABLE = "precip_mm"

CITIES_LIST = ["Palaiseau",
               #"Saint-Jean-de-Chevelu",
               #"Bordeaux",
               #"Nice",
               #"Saint Malo",
               #"Brest France"
               ]