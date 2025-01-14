API_URL = 'http://api.weatherapi.com/v1'
KAFKA_BROKER = 'localhost:9092'
DATA_DIR = './data'
MAX_HISTORY_DAYS = 7
# ARCHIVE_DIR = './archives'
# WAIT_TIME = 10

VARIABLES_TO_KEEP = ["temp_c",
                    "is_day",
                    "wind_kph",
                    "wind_degree", # later separated into cos and sin
                    "pressure_mb",
                    "humidity",
                    "cloud",
                    "feelslike_c",
                    "windchill_c",
                    "heatindex_c",
                    "dewpoint_c",
                    "vis_km",
                    "gust_kph",
                    "uv",
                    "lat",
                    "lon"
]

TARGET_VARIABLE = "precip_mm"

CITIES_LIST = ["Palaiseau",
               "Saint-Jean-de-Chevelu",
               #"Bordeaux",
               #"Nice",
               #"Saint Malo",
               #"Brest France"
               ]