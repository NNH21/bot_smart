import datetime
import re
from config import ASSISTANT_NAME, SPEECH_RATE, LAST_DATE
from weather import get_weather_forecast, get_weatherapi_forecast
from time_utils import get_time_in_timezone, get_relative_date
from history import get_vietnamese_holiday_info, get_international_holiday_info, get_historical_date_info
from web_utils import open_youtube_video, open_web_search, open_website

def process_command(text):
    global SPEECH_RATE, LAST_DATE
    text_lower = text.lower().strip()
    detailed_keywords = ["giải thích", "chi tiết", "tại sao", "làm thế nào", "cách nào", "thế nào"]
    force_detailed = any(keyword in text_lower for keyword in detailed_keywords)

    if any(keyword in text_lower for keyword in ["nhiệt độ", "thời tiết"]):
        city = "Da Nang"
        date = None
        default_city_used = True
        location_mapping = {
            "hà nội": "Hanoi", "hà": "Hanoi", "hanoi": "Hanoi",
            "hồ chí minh": "Ho Chi Minh City", "sài gòn": "Ho Chi Minh City", "saigon": "Ho Chi Minh City",
            "đà nẵng": "Da Nang", "danang": "Da Nang",
            "quảng trị": "Quang Tri",
            "huế": "Hue", "thừa thiên huế": "Hue",
            "quảng ninh": "Ha Long", "hạ long": "Ha Long",
            "nha trang": "Nha Trang", "khánh hòa": "Nha Trang",
            "đà lạt": "Da Lat", "lâm đồng": "Da Lat",
            "cần thơ": "Can Tho",
            "hải phòng": "Hai Phong",
            "quy nhơn": "Quy Nhon", "bình định": "Quy Nhon",
            "buôn ma thuột": "Buon Ma Thuot", "đắk lắk": "Buon Ma Thuot",
            "an giang": "An Giang", "long xuyên": "An Giang",
            "bà rịa vũng tàu": "Vung Tau", "vũng tàu": "Vung Tau",
            "bắc giang": "Bac Giang",
            "bắc kạn": "Bac Kan",
            "bạc liêu": "Bac Lieu",
            "bắc ninh": "Bac Ninh",
            "bến tre": "Ben Tre",
            "bình dương": "Binh Duong", "thủ dầu một": "Binh Duong",
            "bình phước": "Binh Phuoc", "đồng xoài": "Binh Phuoc",
            "bình thuận": "Binh Thuan", "phan thiết": "Binh Thuan",
            "cà mau": "Ca Mau",
            "cao bằng": "Cao Bang",
            "đắk nông": "Dak Nong", "gia nghĩa": "Dak Nong",
            "điện biên": "Dien Bien", "điện biên phủ": "Dien Bien",
            "đồng nai": "Dong Nai", "biên hòa": "Dong Nai",
            "đồng tháp": "Dong Thap", "cao lãnh": "Dong Thap", "sa đéc": "Dong Thap",
            "gia lai": "Gia Lai", "pleiku": "Gia Lai",
            "hà giang": "Ha Giang",
            "hà nam": "Ha Nam", "phủ lý": "Ha Nam",
            "hà tĩnh": "Ha Tinh",
            "hải dương": "Hai Duong",
            "hậu giang": "Hau Giang", "vị thanh": "Hau Giang",
            "hòa bình": "Hoa Binh",
            "hưng yên": "Hung Yen",
            "kiên giang": "Kien Giang", "rạch giá": "Kien Giang", "phú quốc": "Phu Quoc",
            "kon tum": "Kon Tum",
            "lai châu": "Lai Chau",
            "lạng sơn": "Lang Son",
            "lào cai": "Lao Cai", "sapa": "Lao Cai", "sa pa": "Lao Cai",
            "long an": "Long An", "tân an": "Long An",
            "nam định": "Nam Dinh",
            "nghệ an": "Nghe An", "vinh": "Nghe An",
            "ninh bình": "Ninh Binh",
            "ninh thuận": "Ninh Thuan", "phan rang": "Ninh Thuan",
            "phú thọ": "Phu Tho", "việt trì": "Phu Tho",
            "phú yên": "Phu Yen", "tuy hòa": "Phu Yen",
            "quảng bình": "Quang Binh", "đồng hới": "Quang Binh",
            "quảng nam": "Quang Nam", "hội an": "Hoi An", "tam kỳ": "Quang Nam",
            "quảng ngãi": "Quang Ngai",
            "sóc trăng": "Soc Trang",
            "sơn la": "Son La",
            "tây ninh": "Tay Ninh",
            "thái bình": "Thai Binh",
            "thái nguyên": "Thai Nguyen",
            "thanh hóa": "Thanh Hoa",
            "tiền giang": "Tien Giang", "mỹ tho": "Tien Giang",
            "trà vinh": "Tra Vinh",
            "tuyên quang": "Tuyen Quang",
            "vĩnh long": "Vinh Long",
            "vĩnh phúc": "Vinh Phuc", "vĩnh yên": "Vinh Phuc",
            "yên bái": "Yen Bai"
        }
        display_names = {
            "Hanoi": "Hà Nội",
            "Ho Chi Minh City": "Hồ Chí Minh",
            "Da Nang": "Đà Nẵng",
            "Quang Tri": "Quảng Trị",
            "Hue": "Huế",
            "Ha Long": "Quảng Ninh",
            "Nha Trang": "Nha Trang",
            "Da Lat": "Đà Lạt",
            "Can Tho": "Cần Thơ",
            "Hai Phong": "Hải Phòng",
            "Quy Nhon": "Quy Nhơn",
            "Buon Ma Thuot": "Buôn Ma Thuột",
            "An Giang": "An Giang",
            "Vung Tau": "Vũng Tàu",
            "Bac Giang": "Bắc Giang",
            "Bac Kan": "Bắc Kạn",
            "Bac Lieu": "Bạc Liêu",
            "Bac Ninh": "Bắc Ninh",
            "Ben Tre": "Bến Tre",
            "Binh Duong": "Bình Dương",
            "Binh Phuoc": "Bình Phước",
            "Binh Thuan": "Bình Thuận",
            "Ca Mau": "Cà Mau",
            "Cao Bang": "Cao Bằng",
            "Dak Nong": "Đắk Nông",
            "Dien Bien": "Điện Biên",
            "Dong Nai": "Đồng Nai",
            "Dong Thap": "Đồng Tháp",
            "Gia Lai": "Gia Lai",
            "Ha Giang": "Hà Giang",
            "Ha Nam": "Hà Nam",
            "Ha Tinh": "Hà Tĩnh",
            "Hai Duong": "Hải Dương",
            "Hau Giang": "Hậu Giang",
            "Hoa Binh": "Hòa Bình",
            "Hung Yen": "Hưng Yên",
            "Kien Giang": "Kiên Giang",
            "Phu Quoc": "Phú Quốc",
            "Kon Tum": "Kon Tum",
            "Lai Chau": "Lai Châu",
            "Lang Son": "Lạng Sơn",
            "Lao Cai": "Lào Cai",
            "Hoi An": "Hội An",
            "Long An": "Long An",
            "Nam Dinh": "Nam Định",
            "Nghe An": "Nghệ An",
            "Ninh Binh": "Ninh Bình",
            "Ninh Thuan": "Ninh Thuận",
            "Phu Tho": "Phú Thọ",
            "Phu Yen": "Phú Yên",
            "Quang Binh": "Quảng Bình",
            "Quang Nam": "Quảng Nam",
            "Quang Ngai": "Quảng Ngãi",
            "Soc Trang": "Sóc Trăng",
            "Son La": "Sơn La",
            "Tay Ninh": "Tây Ninh",
            "Thai Binh": "Thái Bình",
            "Thai Nguyen": "Thái Nguyên",
            "Thanh Hoa": "Thanh Hóa",
            "Tien Giang": "Tiền Giang",
            "Tra Vinh": "Trà Vinh",
            "Tuyen Quang": "Tuyên Quang",
            "Vinh Long": "Vĩnh Long",
            "Vinh Phuc": "Vĩnh Phúc",
            "Yen Bai": "Yên Bái"
        }

        date_match = re.search(r'(ngày mai|hôm qua|ngày \d+\s*tháng\s*\d+)', text_lower)
        if date_match:
            date_str = date_match.group(0)
            if date_str == "ngày mai":
                date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            elif date_str == "hôm qua":
                date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                day_month = re.search(r'ngày (\d+)\s*tháng\s*(\d+)', date_str)
                if day_month:
                    day, month = map(int, day_month.groups())
                    date = datetime.datetime.now().replace(day=day, month=month).strftime("%Y-%m-%d")

        found_location = False
        for keyword in ["ở", "tại", "của"]:
            if keyword in text_lower and not found_location:
                parts = text_lower.split(keyword, 1)
                if len(parts) > 1:
                    location_part = parts[1].strip()
                    for loc_key in location_mapping.keys():
                        if loc_key in location_part:
                            city = location_mapping[loc_key]
                            default_city_used = False
                            found_location = True
                            break

        if default_city_used:
            for loc_key in location_mapping.keys():
                if loc_key in text_lower:
                    city = location_mapping[loc_key]
                    default_city_used = False
                    found_location = True
                    break

        city_display_name = display_names.get(city, city)

        weather_data = get_weather_forecast(city, date)
        if not weather_data:
            weather_data = get_weatherapi_forecast(city, date)

        if weather_data:
            if date:
                temp_min = weather_data.get("temp_min", "N/A")
                temp_max = weather_data.get("temp_max", "N/A")
                description = weather_data.get("description", "không xác định").capitalize()
                humidity = weather_data.get("humidity", "N/A")
                rain_prob = weather_data.get("rain_prob", "N/A")
                response = f"Dự báo thời tiết tại {city_display_name} vào {date}: "
                response += f"Nhiệt độ từ {temp_min}°C đến {temp_max}°C, {description}, độ ẩm {humidity}%, "
                response += f"xác suất mưa {rain_prob}%."
            else:
                temp = weather_data.get("temp", "N/A")
                feels_like = weather_data.get("feels_like", "N/A")
                humidity = weather_data.get("humidity", "N/A")
                condition = weather_data.get("description", "không xác định").capitalize()
                response = f"Nhiệt độ hiện tại ở {city_display_name} là {temp}°C. {condition}. "
                response += f"Cảm giác như {feels_like}°C. Độ ẩm: {humidity}%."
            return response

        return f"Không thể lấy thông tin thời tiết cho {city_display_name}. Vui lòng thử lại hoặc kiểm tra tên địa điểm."

    day_month_match = re.search(r'ngày (\d+)\s*(tháng|[/\-._])\s*(\d+)', text_lower)
    if day_month_match:
        day = int(day_month_match.group(1))
        month = int(day_month_match.group(3))
        try:
            LAST_DATE = datetime.datetime.now().replace(day=day, month=month)
            holiday_info = get_vietnamese_holiday_info(day, month)
            if holiday_info:
                return f"Ngày {day} tháng {month} là {holiday_info}"
            return f"Ngày {day} tháng {month} không phải là ngày lễ chính thức ở Việt Nam."
        except ValueError:
            return "Ngày hoặc tháng không hợp lệ. Vui lòng kiểm tra lại."

    holiday_info = get_international_holiday_info(text_lower)
    if holiday_info:
        return holiday_info

    if any(keyword in text_lower for keyword in [
        "hôm qua", "hôm nay", "ngày mai", "ngày kia", "ngày mốt",
        "tuần trước", "tuần này", "tuần sau", "tháng trước", "tháng này", "tháng sau"
    ]):
        relative_date = get_relative_date(text_lower)
        LAST_DATE = relative_date
        response = f"Ngày {relative_date.day} tháng {relative_date.month} năm {relative_date.year}"
        holiday_info = get_vietnamese_holiday_info(relative_date.day, relative_date.month)
        if holiday_info:
            response += f". Đây cũng là {holiday_info}"
        return response

    if any(phrase in text_lower for phrase in [
        "ngày mấy", "ngày bao nhiêu", "ngày tháng", "hôm nay là ngày", "hôm nay ngày"
    ]):
        now = datetime.datetime.now()
        LAST_DATE = now
        response = f"Hôm nay là ngày {now.day} tháng {now.month} năm {now.year}"
        holiday_info = get_vietnamese_holiday_info(now.day, now.month)
        if holiday_info:
            response += f". Đây cũng là {holiday_info}"
        return response

    if any(pattern in text_lower for pattern in [
        "thời gian ở", "giờ ở", "mấy giờ ở", "bây giờ là mấy giờ ở"
    ]):
        city = None
        for pattern in ["thời gian ở", "giờ ở", "mấy giờ ở", "bây giờ là mấy giờ ở"]:
            if pattern in text_lower:
                parts = text_lower.split(pattern, 1)
                if len(parts) > 1:
                    city = parts[1].strip()
                    break
        if city:
            return get_time_in_timezone(city)
        return "Vui lòng nói rõ tên thành phố hoặc quốc gia."

    if any(keyword in text_lower for keyword in ["mấy giờ", "thời gian"]) and not any(
        location_word in text_lower for location_word in ["ở", "tại", "của"]
    ):
        now = datetime.datetime.now()
        return f"Bây giờ là {now.hour} giờ {now.minute} phút"

    if any(keyword in text_lower for keyword in ["nói chậm hơn", "chậm lại", "giảm tốc độ nói"]):
        if SPEECH_RATE > 0.4:
            SPEECH_RATE -= 0.2
        return f"Đã giảm tốc độ nói. Tốc độ hiện tại là {int(SPEECH_RATE*100)}%"

    if any(keyword in text_lower for keyword in ["nói nhanh hơn", "nhanh lên", "tăng tốc độ nói"]):
        if SPEECH_RATE < 1.8:
            SPEECH_RATE += 0.2
        return f"Đã tăng tốc độ nói. Tốc độ hiện tại là {int(SPEECH_RATE*100)}%"

    if any(keyword in text_lower for keyword in ["tốc độ nói mặc định", "nói bình thường", "đặt lại tốc độ"]):
        SPEECH_RATE = 1.0
        return "Đã đặt lại tốc độ nói về mức bình thường"

    if any(event_keyword in text_lower for event_keyword in [
        "chiến tranh thế giới", "thế chiến", "11/9", "911", "tháp đôi", 
        "mặt trăng", "neil armstrong", "apollo", "bức tường berlin", 
        "liên minh châu âu", "cách mạng pháp", "cách mạng nga"
    ]):
        historical_info = get_historical_date_info(text)
        if historical_info:
            return historical_info
        return "Xin lỗi, tôi không có thông tin về sự kiện này."

    if any(keyword in text_lower for keyword in ["mở bài hát", "nghe bài", "phát bài", "bài hát"]):
        song_query = text
        for prefix in ["mở bài hát", "nghe bài", "phát bài", "bài hát"]:
            if prefix in text_lower:
                song_parts = text_lower.split(prefix, 1)
                if len(song_parts) > 1:
                    song_query = song_parts[1].strip()
                    break
        if song_query == text:
            return "Vui lòng nói rõ tên bài hát."
        if open_youtube_video(song_query):
            return f"Đang tìm bài hát {song_query} trên YouTube."
        return f"Không tìm thấy bài hát '{song_query}'. Vui lòng thử tên khác hoặc kiểm tra kết nối mạng."

    if any(keyword in text_lower for keyword in ["mở phim", "xem phim", "chiếu phim"]):
        movie_query = text
        for prefix in ["mở phim", "xem phim", "chiếu phim"]:
            if prefix in text_lower:
                movie_parts = text_lower.split(prefix, 1)
                if len(movie_parts) > 1:
                    movie_query = movie_parts[1].strip()
                    break
        if movie_query == text:
            return "Vui lòng nói rõ tên phim."
        if open_youtube_video(movie_query):
            return f"Đang tìm phim {movie_query} trên YouTube."
        return f"Không tìm thấy phim '{movie_query}'. Vui lòng thử tên khác hoặc kiểm tra kết nối mạng."

    if any(keyword in text_lower for keyword in ["tìm kiếm", "tìm thông tin", "tra cứu", "google"]):
        search_query = text
        for prefix in ["tìm kiếm", "tìm thông tin", "tra cứu", "google"]:
            if prefix in text_lower:
                search_parts = text_lower.split(prefix, 1)
                if len(search_parts) > 1:
                    search_query = search_parts[1].strip()
                    break
        if search_query == text:
            return "Vui lòng nói rõ nội dung tìm kiếm."
        if open_web_search(search_query):
            return f"Đang tìm kiếm thông tin về {search_query} trên Google."
        return "Không thể mở trình duyệt để tìm kiếm."

    if any(keyword in text_lower for keyword in ["mở trang", "truy cập", "vào trang", "mở web", "mở"]):
        website = text
        for prefix in ["mở trang", "truy cập", "vào trang", "mở web", "mở"]:
            if prefix in text_lower:
                web_parts = text_lower.split(prefix, 1)
                if len(web_parts) > 1:
                    website = web_parts[1].strip()
                    break
        return open_website(website)

    # Xử lý truy vấn về tên hoặc danh tính của trợ lý
    name_queries = ["bạn tên là gì", "tên của bạn", "bạn là ai", "tên bạn là gì"]
    if any(query in text_lower for query in name_queries):
        return f"Tôi là {ASSISTANT_NAME}"

    return "Xin lỗi, tôi chưa hiểu yêu cầu của bạn. Vui lòng thử lại."