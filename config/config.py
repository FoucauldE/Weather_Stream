API_URL = 'http://api.weatherapi.com/v1'
KAFKA_BROKER = 'localhost:9092'
DATA_DIR = './data'
MAX_HISTORY_DAYS = 7

VARIABLES_TO_KEEP = ["cloud",
                     "pressure_mb",
                     "humidity",
                     "dewpoint_c",
                     "vis_km",
                     "wind_kph",
                     "temp_c",
                     "lat",
                     "lon"]

SELECTED_FEATURES = ["cloud",
                     "pressure_mb",
                     "humidity",
                     "dewpoint_c",
                     "vis_km",
                     "wind_kph",
                     "temp_c",
                     "wind_degree_sin",
                     "wind_degree_cos",
                     "lat",
                     "lon",
                     "prev_target"]

TARGET_VARIABLE = "precip_mm"

CITIES_LIST = ["Palaiseau",
               "Lyon",
               "Bordeaux",
               "Nice",
               "Saint Malo",
               "Brest France",
               "Paris",
               "Nantes",
               "Strasbourg",
               "Marseille",
               "Toulouse",
               "Calais",
               "Clermont-Ferrand",
               "La Rochelle",
               "Le Mans",
               "Troyes",
               "Orléans",
               "Biarritz",
               "Perpignan",
               "Limoges",
               "Châteauroux"
               ]