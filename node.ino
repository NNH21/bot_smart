#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>
#include <ArduinoJson.h>

// Khai báo LCD với địa chỉ I2C (thay đổi nếu cần)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Cấu hình WiFi
const char* ssid = "60 DO CUNG";
const char* password = "0903477114";

// OpenWeatherMap API Key
const String weatherApiKey = "292afcea31e70049e0995db453d7fca6";
const String defaultCity = "Hanoi";

// Pin microphone (không sử dụng trong mã này, nhưng giữ lại để tương thích)
const int microphonePin = A0;

// Khai báo hàm getWeather trước khi sử dụng
String getWeather(String city, int retries = 2);

void setup() {
  Serial.begin(115200);
  Wire.begin(D2, D1); // SDA = D2, SCL = D1 trên ESP8266 (có thể thay đổi tùy board)
  
  // Khởi tạo LCD
  lcd.init();
  lcd.backlight();
  lcd.print("Tro ly ao");
  lcd.setCursor(0, 1);
  lcd.print("Dang khoi dong...");
  
  // Kết nối WiFi
  WiFi.begin(ssid, password);
  int wifi_attempts = 0;
  while (WiFi.status() != WL_CONNECTED && wifi_attempts < 20) {
    delay(500);
    Serial.print(".");
    wifi_attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    lcd.clear();
    lcd.print("Da ket noi WiFi");
    lcd.setCursor(0, 1);
    lcd.print(WiFi.localIP().toString());
    delay(2000);
  } else {
    lcd.clear();
    lcd.print("Khong ket noi WiFi");
    delay(2000);
  }

  lcd.clear();
  lcd.print("San sang nhan");
  lcd.setCursor(0, 1);
  lcd.print("lenh...");
}

void loop() {
  if (Serial.available()) {
    String message = Serial.readStringUntil('\n');
    message.trim();
    
    if (message.startsWith("WEATHER:")) {
      String city = message.substring(8);
      city.trim();
      
      lcd.clear();
      lcd.print("Query weather:");
      lcd.setCursor(0, 1);
      lcd.print(city);
      
      if (city.length() == 0) {
        city = defaultCity;
        lcd.clear();
        lcd.print("Using default:");
        lcd.setCursor(0, 1);
        lcd.print(defaultCity);
        delay(1000);
      }
      
      String weatherInfo = getWeather(city);
      Serial.println("WEATHER_RESPONSE:" + weatherInfo);
      displayOnLCD(weatherInfo);
    } else {
      displayOnLCD(message);
    }
  }
}

void displayOnLCD(String message) {
  lcd.clear();
  if (message.length() <= 16) {
    lcd.print(message);
  } else {
    lcd.print(message.substring(0, 16));
    lcd.setCursor(0, 1);
    lcd.print(message.substring(16, min((int)message.length(), 32)));
    
    if (message.length() > 32) {
      delay(2000);
      for (int i = 0; i < message.length() - 32; i++) {
        lcd.clear();
        lcd.print(message.substring(i + 1, min(i + 17, (int)message.length())));
        lcd.setCursor(0, 1);
        lcd.print(message.substring(i + 17, min(i + 33, (int)message.length())));
        delay(300);
      }
    }
  }
}

String urlEncode(String str) {
  String encodedString = "";
  char c;
  char code0;
  char code1;
  for (int i = 0; i < str.length(); i++) {
    c = str.charAt(i);
    if (c == ' ') {
      encodedString += '+';
    } else if (isalnum(c)) {
      encodedString += c;
    } else {
      code1 = (c & 0xf) + '0';
      if ((c & 0xf) > 9) {
        code1 = (c & 0xf) - 10 + 'A';
      }
      c = (c >> 4) & 0xf;
      code0 = c + '0';
      if (c > 9) {
        code0 = c - 10 + 'A';
      }
      encodedString += '%';
      encodedString += code0;
      encodedString += code1;
    }
  }
  return encodedString;
}

String getWeather(String city, int retries) {
  if (WiFi.status() != WL_CONNECTED) {
    displayOnLCD("Khong ket noi WiFi");
    return "Không có kết nối WiFi";
  }
  
  WiFiClient client;
  HTTPClient http;
  
  String encodedCity = urlEncode(city);
  String cityName = city;
  
  // Danh sách tên thay thế cho các địa điểm
  String alternativeCities[] = {
    city,  // Thành phố gốc
    city == "Quang Ninh" ? "Ha Long" : city,  // Thay thế cho Quảng Ninh
    city == "Hoi An" ? "Hội An" : city,
    city == "Phu Quoc" ? "Phú Quốc" : city
  };
  
  for (int attempt = 0; attempt < retries; attempt++) {
    for (int i = 0; i < (sizeof(alternativeCities) / sizeof(alternativeCities[0])); i++) {
      encodedCity = urlEncode(alternativeCities[i]);
      String currentUrl = "http://api.openweathermap.org/data/2.5/weather?q=" + encodedCity + ",VN&appid=" + weatherApiKey + "&units=metric&lang=vi";
      
      Serial.print("Calling Current Weather URL: ");
      Serial.println(currentUrl);
      
      http.begin(client, currentUrl);
      int httpCode = http.GET();
      
      Serial.print("HTTP Status: ");
      Serial.println(httpCode);
      
      if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        DynamicJsonDocument doc(1024);
        DeserializationError error = deserializeJson(doc, payload);
        if (error) {
          http.end();
          displayOnLCD("Loi phan tich JSON");
          return "Lỗi phân tích JSON";
        }
        
        float temp = doc["main"]["temp"];
        float feelsLike = doc["main"]["feels_like"];
        float tempMin = doc["main"]["temp_min"];
        float tempMax = doc["main"]["temp_max"];
        if (tempMin == tempMax) {
          tempMin = temp - 0.5;
          tempMax = temp + 0.5;
        }
        int humidity = doc["main"]["humidity"];
        String description = doc["weather"][0]["description"];
        float windSpeed = 0;
        int windDeg = 0;
        if (doc.containsKey("wind")) {
          windSpeed = doc["wind"]["speed"];
          if (doc["wind"].containsKey("deg")) {
            windDeg = doc["wind"]["deg"];
          }
        }
        cityName = doc["name"].as<String>();
        
        http.end();
        
        float lat = doc["coord"]["lat"];
        float lon = doc["coord"]["lon"];
        String oneCallUrl = "https://api.openweathermap.org/data/2.5/onecall?lat=" + String(lat) + "&lon=" + String(lon) + "&exclude=minutely,hourly&appid=" + weatherApiKey + "&units=metric&lang=vi";
        
        Serial.print("Calling OneCall API URL: ");
        Serial.println(oneCallUrl);
        
        http.begin(client, oneCallUrl);
        httpCode = http.GET();
        
        float uvIndex = -1;
        int rainDayProbability = -1;
        int rainNightProbability = -1;
        
        if (httpCode == HTTP_CODE_OK) {
          payload = http.getString();
          DynamicJsonDocument forecastDoc(6144);
          error = deserializeJson(forecastDoc, payload);
          if (!error) {
            if (forecastDoc["current"].containsKey("uvi")) {
              uvIndex = forecastDoc["current"]["uvi"];
            }
            if (forecastDoc.containsKey("daily") && forecastDoc["daily"].size() > 0) {
              JsonArray daily = forecastDoc["daily"];
              if (daily[0].containsKey("pop")) {
                rainDayProbability = daily[0]["pop"].as<float>() * 100;
              }
              if (daily.size() > 1 && daily[1].containsKey("pop")) {
                rainNightProbability = daily[0]["pop"].as<float>() * 100;
              }
            }
          }
        }
        
        http.end();
        
        String windDirection = "";
        if (windSpeed < 0.5) {
          windDirection = "không có gió";
        } else {
          if (windDeg >= 337.5 || windDeg < 22.5) windDirection = "Bắc";
          else if (windDeg >= 22.5 && windDeg < 67.5) windDirection = "Đông Bắc";
          else if (windDeg >= 67.5 && windDeg < 112.5) windDirection = "Đông";
          else if (windDeg >= 112.5 && windDeg < 157.5) windDirection = "Đông Nam";
          else if (windDeg >= 157.5 && windDeg < 202.5) windDirection = "Nam";
          else if (windDeg >= 202.5 && windDeg < 247.5) windDirection = "Tây Nam";
          else if (windDeg >= 247.5 && windDeg < 292.5) windDirection = "Tây";
          else if (windDeg >= 292.5 && windDeg < 337.5) windDirection = "Tây Bắc";
        }
        
        String uvDescription = "";
        if (uvIndex == -1) {
          int currentHour = doc["dt"].as<long>() % 86400 / 3600 + 7;
          if (currentHour >= 10 && currentHour <= 16) {
            uvDescription = "trung bình đến cao (ước tính)";
          } else if ((currentHour >= 7 && currentHour < 10) || (currentHour > 16 && currentHour <= 18)) {
            uvDescription = "thấp đến trung bình (ước tính)";
          } else {
            uvDescription = "thấp hoặc không có (ước tính)";
          }
        } else if (uvIndex < 3) uvDescription = "thấp";
        else if (uvIndex < 6) uvDescription = "trung bình";
        else if (uvIndex < 8) uvDescription = "cao";
        else if (uvIndex < 11) uvDescription = "rất cao";
        else uvDescription = "nguy hiểm";
        
        if (rainDayProbability == -1) {
          int clouds = 0;
          if (doc.containsKey("clouds") && doc["clouds"].containsKey("all")) {
            clouds = doc["clouds"]["all"];
          }
          String weatherDesc = doc["weather"][0]["main"];
          if (weatherDesc.indexOf("rain") >= 0 || weatherDesc.indexOf("Rain") >= 0) {
            rainDayProbability = 80;
            rainNightProbability = 70;
          } else if (clouds > 75) {
            rainDayProbability = 40;
            rainNightProbability = 30;
          } else if (clouds > 50) {
            rainDayProbability = 20;
            rainNightProbability = 15;
          } else {
            rainDayProbability = 5;
            rainNightProbability = 5;
          }
        }
        
        DynamicJsonDocument responseDoc(1024);
        responseDoc["temp"] = temp;
        responseDoc["feels_like"] = feelsLike;
        responseDoc["temp_min"] = tempMin;
        responseDoc["temp_max"] = tempMax;
        responseDoc["humidity"] = humidity;
        responseDoc["description"] = description;
        responseDoc["wind_speed"] = windSpeed;
        responseDoc["wind_direction"] = windDirection;
        responseDoc["uv_index"] = uvIndex;
        responseDoc["uv_description"] = uvDescription;
        responseDoc["rain_day"] = rainDayProbability;
        responseDoc["rain_night"] = rainNightProbability;
        responseDoc["city_name"] = cityName;
        
        String jsonResponse;
        serializeJson(responseDoc, jsonResponse);
        
        return jsonResponse;
      } else {
        http.end();
        Serial.print("Lỗi API: ");
        Serial.println(httpCode);
        displayOnLCD("Loi API: " + String(httpCode));
        delay(1000);
      }
    }
    
    // Thử với geocoding nếu tất cả tên thành phố thất bại
    String geoUrl = "http://api.openweathermap.org/geo/1.0/direct?q=" + encodedCity + ",VN&limit=1&appid=" + weatherApiKey;
    http.begin(client, geoUrl);
    int geoCode = http.GET();
    
    if (geoCode == HTTP_CODE_OK) {
      String geoPayload = http.getString();
      DynamicJsonDocument geoDoc(512);
      DeserializationError geoError = deserializeJson(geoDoc, geoPayload);
      if (!geoError && geoDoc.size() > 0) {
        float lat = geoDoc[0]["lat"];
        float lon = geoDoc[0]["lon"];
        cityName = geoDoc[0]["name"].as<String>();
        
        http.end();
        
        String oneCallUrl = "https://api.openweathermap.org/data/2.5/onecall?lat=" + String(lat) + "&lon=" + String(lon) + "&exclude=minutely,hourly&appid=" + weatherApiKey + "&units=metric&lang=vi";
        http.begin(client, oneCallUrl);
        int httpCode = http.GET();
        
        if (httpCode == HTTP_CODE_OK) {
          String payload = http.getString();
          DynamicJsonDocument doc(6144);
          DeserializationError error = deserializeJson(doc, payload);
          if (!error) {
            float temp = doc["current"]["temp"];
            float feelsLike = doc["current"]["feels_like"];
            float tempMin = temp - 0.5;
            float tempMax = temp + 0.5;
            int humidity = doc["current"]["humidity"];
            String description = doc["current"]["weather"][0]["description"];
            float windSpeed = doc["current"]["wind_speed"];
            int windDeg = doc["current"]["wind_deg"];
            float uvIndex = doc["current"]["uvi"];
            int rainDayProbability = doc["daily"][0]["pop"].as<float>() * 100;
            int rainNightProbability = doc["daily"][0]["pop"].as<float>() * 100;
            
            String windDirection = "";
            if (windSpeed < 0.5) {
              windDirection = "không có gió";
            } else {
              if (windDeg >= 337.5 || windDeg < 22.5) windDirection = "Bắc";
              else if (windDeg >= 22.5 && windDeg < 67.5) windDirection = "Đông Bắc";
              else if (windDeg >= 67.5 && windDeg < 112.5) windDirection = "Đông";
              else if (windDeg >= 112.5 && windDeg < 157.5) windDirection = "Đông Nam";
              else if (windDeg >= 157.5 && windDeg < 202.5) windDirection = "Nam";
              else if (windDeg >= 202.5 && windDeg < 247.5) windDirection = "Tây Nam";
              else if (windDeg >= 247.5 && windDeg < 292.5) windDirection = "Tây";
              else if (windDeg >= 292.5 && windDeg < 337.5) windDirection = "Tây Bắc";
            }
            
            String uvDescription = "";
            if (uvIndex < 3) uvDescription = "thấp";
            else if (uvIndex < 6) uvDescription = "trung bình";
            else if (uvIndex < 8) uvDescription = "cao";
            else if (uvIndex < 11) uvDescription = "rất cao";
            else uvDescription = "nguy hiểm";
            
            DynamicJsonDocument responseDoc(1024);
            responseDoc["temp"] = temp;
            responseDoc["feels_like"] = feelsLike;
            responseDoc["temp_min"] = tempMin;
            responseDoc["temp_max"] = tempMax;
            responseDoc["humidity"] = humidity;
            responseDoc["description"] = description;
            responseDoc["wind_speed"] = windSpeed;
            responseDoc["wind_direction"] = windDirection;
            responseDoc["uv_index"] = uvIndex;
            responseDoc["uv_description"] = uvDescription;
            responseDoc["rain_day"] = rainDayProbability;
            responseDoc["rain_night"] = rainNightProbability;
            responseDoc["city_name"] = cityName;
            
            String jsonResponse;
            serializeJson(responseDoc, jsonResponse);
            
            http.end();
            return jsonResponse;
          }
        }
        http.end();
      }
      http.end();
    }
    
    delay(1000);
  }
  
  return "Không thể lấy thời tiết cho " + city;
}