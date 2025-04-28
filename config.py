import requests
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Cấu hình cho trợ lý ảo
ASSISTANT_NAME = "Mis"
WAKE_WORDS = ["hey mít", "hây mít", "hey mit", "hay mit", "hây mis", "hey mít", 
             "hay mít", "này mít", "này mit", "hey me", "hây mi", "hi mít", 
             "hi mit", "hey miss", "hây mi", "này mi", "n mít", "mít ơi", 
             "mít ơi", "mit ơi", "xin chào mít", "chào mít", "mít", "mit"]
waiting_for_command = False
REQUIRE_WAKE_WORD = False
SPEECH_RATE = 1.2  # Tăng tốc độ từ 1.0 lên 1.2

# API Keys
OPENWEATHERMAP_API_KEY = "292afcea31e70049e0995db453d7fca6"
TIMEZONEDB_API_KEY = "NIS9LQW9KOHB"
WEATHERAPI_KEY = "8c587eb97df52089f5566f5a54eda437"
GEMINI_API_KEY = "AIzaSyD7w3vcBaJO4yx4KP3LLxEjYPdZGGpPcUU"  # API Key của Gemini

# Cache thời tiết
weather_cache = {}  # {key: (response, timestamp)}
CACHE_TIMEOUT = 300  # 5 phút

# Session HTTP để giữ kết nối mở
session = requests.Session()

# Biến toàn cục
LAST_DATE = None