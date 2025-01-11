API_URL = 'http://api.weatherapi.com/v1'
KAFKA_BROKER = 'localhost:9092'
# ARCHIVE_DIR = './archives'
# WAIT_TIME = 10

VARIABLES_TO_KEEP = ["temp_c",
                    "is_day",
                    "wind_kph",
                    "wind_degree", # use cos and sin
                    # "wind_dir",
                    "pressure_mb",
                    "humidity",
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