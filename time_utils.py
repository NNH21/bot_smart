import datetime
import requests
import pytz
import logging
from config import session, TIMEZONEDB_API_KEY

def get_relative_date(date_type):
    today = datetime.datetime.now()
    relative_days = {
        "hôm qua": -1, "hôm kia": -2, "hôm trước": -1, "ngày trước": -1, 
        "ngày hôm qua": -1, "ngày hôm kia": -2, "ngày hôm trước": -1,
        "hôm nay": 0, "ngày hôm nay": 0, "ngày mai": 1, "ngày kia": 2,
        "ngày mốt": 2, "hôm tới": 1
    }
    relative_weeks = {
        "tuần trước": -1, "tuần vừa rồi": -1, "tuần qua": -1,
        "tuần này": 0, "tuần hiện tại": 0, "tuần sau": 1, "tuần tới": 1
    }
    relative_months = {
        "tháng trước": -1, "tháng vừa rồi": -1, "tháng qua": -1,
        "tháng này": 0, "tháng hiện tại": 0, "tháng sau": 1, "tháng tới": 1
    }
    days_delta = 0
    for key, value in relative_days.items():
        if key in date_type.lower():
            days_delta = value
            break
    for key, value in relative_weeks.items():
        if key in date_type.lower():
            days_delta = value * 7
            break
    for key, value in relative_months.items():
        if key in date_type.lower():
            new_date = today.replace(day=1)
            if value > 0:
                if today.month + value <= 12:
                    new_date = new_date.replace(month=today.month + value)
                else:
                    new_date = new_date.replace(year=today.year + 1, month=(today.month + value) % 12 or 12)
            else:
                if today.month + value > 0:
                    new_date = new_date.replace(month=today.month + value)
                else:
                    new_date = new_date.replace(year=today.year - 1, month=12 + (today.month + value))
            try:
                new_date = new_date.replace(day=min(today.day, [31, 29 if new_date.year % 4 == 0 and (new_date.year % 100 != 0 or new_date.year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][new_date.month - 1]))
            except:
                next_month = new_date.replace(month=new_date.month + 1, day=1) if new_date.month < 12 else new_date.replace(year=new_date.year + 1, month=1, day=1)
                new_date = next_month - datetime.timedelta(days=1)
            return new_date
    if days_delta != 0:
        return today + datetime.timedelta(days=days_delta)
    return today

def get_time_in_timezone(location_name):
    location = location_name.lower().strip()
    location_mapping = {
        "hà nội": "Asia/Ho_Chi_Minh", "hà": "Asia/Ho_Chi_Minh", "hanoi": "Asia/Ho_Chi_Minh",
        "hồ chí minh": "Asia/Ho_Chi_Minh", "sài gòn": "Asia/Ho_Chi_Minh", "saigon": "Asia/Ho_Chi_Minh",
        "đà nẵng": "Asia/Ho_Chi_Minh", "danang": "Asia/Ho_Chi_Minh",
        "quảng trị": "Asia/Ho_Chi_Minh",
        "huế": "Asia/Ho_Chi_Minh", "thừa thiên huế": "Asia/Ho_Chi_Minh",
        "quảng ninh": "Asia/Ho_Chi_Minh", "hạ long": "Asia/Ho_Chi_Minh",
        "nha trang": "Asia/Ho_Chi_Minh", "khánh hòa": "Asia/Ho_Chi_Minh",
        "đà lạt": "Asia/Ho_Chi_Minh", "lâm đồng": "Asia/Ho_Chi_Minh",
        "cần thơ": "Asia/Ho_Chi_Minh",
        "hải phòng": "Asia/Ho_Chi_Minh",
        "quy nhơn": "Asia/Ho_Chi_Minh", "bình định": "Asia/Ho_Chi_Minh",
        "buôn ma thuột": "Asia/Ho_Chi_Minh", "đắk lắk": "Asia/Ho_Chi_Minh",
        "an giang": "Asia/Ho_Chi_Minh", "long xuyên": "Asia/Ho_Chi_Minh",
        "bà rịa vũng tàu": "Asia/Ho_Chi_Minh", "vũng tàu": "Asia/Ho_Chi_Minh",
        "bắc giang": "Asia/Ho_Chi_Minh",
        "bắc kạn": "Asia/Ho_Chi_Minh",
        "bạc liêu": "Asia/Ho_Chi_Minh",
        "bắc ninh": "Asia/Ho_Chi_Minh",
        "bến tre": "Asia/Ho_Chi_Minh",
        "bình dương": "Asia/Ho_Chi_Minh", "thủ dầu một": "Asia/Ho_Chi_Minh",
        "bình phước": "Asia/Ho_Chi_Minh", "đồng xoài": "Asia/Ho_Chi_Minh",
        "bình thuận": "Asia/Ho_Chi_Minh", "phan thiết": "Asia/Ho_Chi_Minh",
        "cà mau": "Asia/Ho_Chi_Minh",
        "cao bằng": "Asia/Ho_Chi_Minh",
        "đắk nông": "Asia/Ho_Chi_Minh", "gia nghĩa": "Asia/Ho_Chi_Minh",
        "điện biên": "Asia/Ho_Chi_Minh", "điện biên phủ": "Asia/Ho_Chi_Minh",
        "đồng nai": "Asia/Ho_Chi_Minh", "biên hòa": "Asia/Ho_Chi_Minh",
        "đồng tháp": "Asia/Ho_Chi_Minh", "cao lãnh": "Asia/Ho_Chi_Minh", "sa đéc": "Asia/Ho_Chi_Minh",
        "gia lai": "Asia/Ho_Chi_Minh", "pleiku": "Asia/Ho_Chi_Minh",
        "hà giang": "Asia/Ho_Chi_Minh",
        "hà nam": "Asia/Ho_Chi_Minh", "phủ lý": "Asia/Ho_Chi_Minh",
        "hà tĩnh": "Asia/Ho_Chi_Minh",
        "hải dương": "Asia/Ho_Chi_Minh",
        "hậu giang": "Asia/Ho_Chi_Minh", "vị thanh": "Asia/Ho_Chi_Minh",
        "hòa bình": "Asia/Ho_Chi_Minh",
        "hưng yên": "Asia/Ho_Chi_Minh",
        "kiên giang": "Asia/Ho_Chi_Minh", "rạch giá": "Asia/Ho_Chi_Minh", "phú quốc": "Asia/Ho_Chi_Minh",
        "kon tum": "Asia/Ho_Chi_Minh",
        "lai châu": "Asia/Ho_Chi_Minh",
        "lạng sơn": "Asia/Ho_Chi_Minh",
        "lào cai": "Asia/Ho_Chi_Minh", "sapa": "Asia/Ho_Chi_Minh", "sa pa": "Asia/Ho_Chi_Minh",
        "long an": "Asia/Ho_Chi_Minh", "tân an": "Asia/Ho_Chi_Minh",
        "nam định": "Asia/Ho_Chi_Minh",
        "nghệ an": "Asia/Ho_Chi_Minh", "vinh": "Asia/Ho_Chi_Minh",
        "ninh bình": "Asia/Ho_Chi_Minh",
        "ninh thuận": "Asia/Ho_Chi_Minh", "phan rang": "Asia/Ho_Chi_Minh",
        "phú thọ": "Asia/Ho_Chi_Minh", "việt trì": "Asia/Ho_Chi_Minh",
        "phú yên": "Asia/Ho_Chi_Minh", "tuy hòa": "Asia/Ho_Chi_Minh",
        "quảng bình": "Asia/Ho_Chi_Minh", "đồng hới": "Asia/Ho_Chi_Minh",
        "quảng nam": "Asia/Ho_Chi_Minh", "hội an": "Asia/Ho_Chi_Minh", "tam kỳ": "Asia/Ho_Chi_Minh",
        "quảng ngãi": "Asia/Ho_Chi_Minh",
        "sóc trăng": "Asia/Ho_Chi_Minh",
        "sơn la": "Asia/Ho_Chi_Minh",
        "tây ninh": "Asia/Ho_Chi_Minh",
        "thái bình": "Asia/Ho_Chi_Minh",
        "thái nguyên": "Asia/Ho_Chi_Minh",
        "thanh hóa": "Asia/Ho_Chi_Minh",
        "tiền giang": "Asia/Ho_Chi_Minh", "mỹ tho": "Asia/Ho_Chi_Minh",
        "trà vinh": "Asia/Ho_Chi_Minh",
        "tuyên quang": "Asia/Ho_Chi_Minh",
        "vĩnh long": "Asia/Ho_Chi_Minh",
        "vĩnh phúc": "Asia/Ho_Chi_Minh", "vĩnh yên": "Asia/Ho_Chi_Minh",
        "yên bái": "Asia/Ho_Chi_Minh",
        "mỹ": "America/New_York",
        "new york": "America/New_York",
        "los angeles": "America/Los_Angeles",
        "chicago": "America/Chicago",
        "toronto": "America/Toronto",
        "mexico": "America/Mexico_City",
        "brazil": "America/Sao_Paulo",
        "argentina": "America/Argentina/Buenos_Aires",
        "anh": "Europe/London",
        "london": "Europe/London",
        "pháp": "Europe/Paris",
        "paris": "Europe/Paris",
        "berlin": "Europe/Berlin",
        "đức": "Europe/Berlin",
        "moscow": "Europe/Moscow",
        "nga": "Europe/Moscow",
        "rome": "Europe/Rome",
        "ý": "Europe/Rome",
        "madrid": "Europe/Madrid",
        "tây ban nha": "Europe/Madrid",
        "nhật": "Asia/Tokyo",
        "nhật bản": "Asia/Tokyo",
        "tokyo": "Asia/Tokyo",
        "trung quốc": "Asia/Shanghai",
        "bắc kinh": "Asia/Shanghai",
        "singapore": "Asia/Singapore",
        "hồng kông": "Asia/Hong_Kong",
        "seoul": "Asia/Seoul",
        "hàn quốc": "Asia/Seoul",
        "bangkok": "Asia/Bangkok",
        "thái lan": "Asia/Bangkok",
        "dubai": "Asia/Dubai",
        "việt nam": "Asia/Ho_Chi_Minh",
        "sydney": "Australia/Sydney",
        "úc": "Australia/Sydney",
        "new zealand": "Pacific/Auckland"
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
        "Yen Bai": "Yên Bái",
        "America/New_York": "New York",
        "America/Los_Angeles": "Los Angeles",
        "America/Chicago": "Chicago",
        "America/Toronto": "Toronto",
        "America/Mexico_City": "Mexico",
        "America/Sao_Paulo": "Brazil (São Paulo)",
        "America/Argentina/Buenos_Aires": "Argentina",
        "Europe/London": "London",
        "Europe/Paris": "Paris",
        "Europe/Berlin": "Berlin",
        "Europe/Moscow": "Moscow",
        "Europe/Rome": "Rome",
        "Europe/Madrid": "Madrid",
        "Asia/Tokyo": "Tokyo",
        "Asia/Shanghai": "Bắc Kinh",
        "Asia/Singapore": "Singapore",
        "Asia/Hong_Kong": "Hồng Kông",
        "Asia/Seoul": "Seoul",
        "Asia/Bangkok": "Bangkok",
        "Asia/Dubai": "Dubai",
        "Asia/Ho_Chi_Minh": "Việt Nam",
        "Australia/Sydney": "Sydney",
        "Pacific/Auckland": "New Zealand"
    }

    try:
        timezone = location_mapping.get(location, 'Etc/UTC')
        url = f"https://api.timezonedb.com/v2.1/get-time-zone?key={TIMEZONEDB_API_KEY}&format=json&by=zone&zone={timezone}"
        response = session.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            formatted_time = data["formatted"]
            display_name = display_names.get(timezone, location_name.capitalize())
            return f"Thời gian hiện tại ở {display_name} là {formatted_time}"
        else:
            logging.error(f"TimeZoneDB API trả về lỗi: {data.get('message', 'Không rõ')}")
            return "Xin lỗi, tôi không thể lấy thời gian lúc này."
    except requests.RequestException as e:
        logging.error(f"Lỗi khi gọi TimeZoneDB API: {e}, Response: {response.text if 'response' in locals() else 'N/A'}")
        try:
            timezone = pytz.timezone(location_mapping.get(location, 'Etc/UTC'))
            current_time = datetime.datetime.now(timezone)
            display_name = display_names.get(location_mapping.get(location, 'Etc/UTC'), location_name.capitalize())
            time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            return f"Thời gian hiện tại ở {display_name} là {time_str}"
        except pytz.exceptions.PytzError as pe:
            logging.error(f"Lỗi dự phòng pytz: {pe}")
            return "Xin lỗi, tôi không thể lấy thời gian lúc này."