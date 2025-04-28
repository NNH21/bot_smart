def get_vietnamese_holiday_info(day, month):
    vietnam_holidays = {
        (1, 1): "Tết Dương lịch - Ngày đầu tiên của năm mới theo lịch Gregorian.",
        (3, 2): "Ngày thành lập Đảng Cộng sản Việt Nam - Kỷ niệm ngày thành lập Đảng Cộng sản Việt Nam (3/2/1930).",
        (8, 3): "Ngày Quốc tế Phụ nữ - Ngày tôn vinh phụ nữ trên toàn thế giới.",
        (10, 3): "Ngày Giỗ Tổ Hùng Vương - Ngày tưởng nhớ các Vua Hùng, được tính theo âm lịch (mùng 10 tháng 3 âm lịch).",
        (30, 4): "Ngày Giải phóng miền Nam, thống nhất đất nước - Kỷ niệm ngày quân đội Việt Nam giải phóng Sài Gòn (30/4/1975).",
        (1, 5): "Ngày Quốc tế Lao động - Ngày của người lao động trên toàn thế giới.",
        (7, 5): "Ngày chiến thắng Điện Biên Phủ - Kỷ niệm chiến thắng lịch sử Điện Biên Phủ (7/5/1954).",
        (19, 5): "Ngày sinh Chủ tịch Hồ Chí Minh - Kỷ niệm ngày sinh của Chủ tịch Hồ Chí Minh (19/5/1890).",
        (1, 6): "Ngày Quốc tế Thiếu nhi - Ngày tôn vinh và bảo vệ quyền trẻ em.",
        (27, 7): "Ngày Thương binh Liệt sĩ - Ngày tưởng nhớ các anh hùng, liệt sĩ đã hy sinh vì độc lập dân tộc.",
        (19, 8): "Ngày Cách mạng tháng Tám thành công - Kỷ niệm Cách mạng tháng Tám năm 1945.",
        (2, 9): "Ngày Quốc khánh - Kỷ niệm ngày Chủ tịch Hồ Chí Minh đọc Tuyên ngôn độc lập (2/9/1945).",
        (20, 10): "Ngày Phụ nữ Việt Nam - Ngày thành lập Hội Liên hiệp Phụ nữ Việt Nam.",
        (20, 11): "Ngày Nhà giáo Việt Nam - Ngày tôn vinh các thầy cô giáo.",
        (22, 12): "Ngày thành lập Quân đội Nhân dân Việt Nam - Kỷ niệm ngày thành lập Quân đội Nhân dân Việt Nam (22/12/1944).",
        (24, 12): "Lễ Giáng sinh - Ngày lễ Giáng sinh được nhiều người Việt Nam tổ chức ăn mừng.",
        (31, 12): "Ngày cuối cùng của năm - Đêm giao thừa Dương lịch."
    }
    return vietnam_holidays.get((day, month))

def get_international_holiday_info(query_text):
    holidays = {
        "halloween": {"date": (31, 10), "description": "Halloween là ngày lễ hóa trang được tổ chức vào ngày 31 tháng 10, phổ biến ở Mỹ và nhiều nước phương Tây."},
        "thanksgiving": {"description": "Lễ Tạ Ơn ở Mỹ thường được tổ chức vào thứ Năm thứ tư của tháng 11.", "dynamic": True},
        "veterans day": {"date": (11, 11), "description": "Ngày Cựu Chiến binh ở Mỹ, được tổ chức vào ngày 11 tháng 11 để tôn vinh những người từng phục vụ trong quân đội."},
        "christmas": {"date": (25, 12), "description": "Lễ Giáng sinh, được tổ chức vào ngày 25 tháng 12 để kỷ niệm sự ra đời của Chúa Giêsu."}
    }
    query_lower = query_text.lower()
    for holiday, info in holidays.items():
        if holiday in query_lower:
            if "date" in info:
                day, month = info["date"]
                return f"{info['description']} Được tổ chức vào ngày {day} tháng {month}."
            return info["description"]
    return None

def get_historical_date_info(query_text):
    historical_events = {
        "chiến tranh thế giới thứ nhất": {
            "bắt đầu": "28/7/1914",
            "kết thúc": "11/11/1918",
            "mô tả": "Cuộc xung đột quân sự toàn cầu bắt đầu tại Châu Âu, dẫn đến cái chết của hàng triệu người."
        },
        "chiến tranh thế giới thứ hai": {
            "bắt đầu": "1/9/1939", 
            "kết thúc": "2/9/1945",
            "mô tả": "Cuộc chiến tranh toàn cầu liên quan đến hầu hết các quốc gia, hình thành hai liên minh quân sự đối lập."
        },
        "sự kiện 11/9": {
            "ngày": "11/9/2001",
            "mô tả": "Loạt các cuộc tấn công khủng bố tại Mỹ bởi tổ chức Al-Qaeda."
        },
        "hạ cánh mặt trăng": {
            "ngày": "20/7/1969",
            "mô tả": "Neil Armstrong trở thành người đầu tiên đặt chân lên Mặt Trăng trong sứ mệnh Apollo 11."
        },
        "bức tường berlin": {
            "xây dựng": "13/8/1961",
            "sụp đổ": "9/11/1989",
            "mô tả": "Biểu tượng của Chiến tranh Lạnh, ngăn cách Tây Berlin và Đông Đức."
        },
        "liên minh châu âu": {
            "thành lập": "1/11/1993",
            "mô tả": "Thành lập chính thức Liên minh Châu Âu (EU) theo Hiệp ước Maastricht."
        },
        "cách mạng pháp": {
            "bắt đầu": "14/7/1789",
            "kết thúc": "9/11/1799",
            "mô tả": "Thời kỳ xáo trộn xã hội và chính trị sâu sắc tại Pháp."
        },
        "cách mạng nga": {
            "tháng 2": "8/3/1917",
            "tháng 10": "7/11/1917",
            "mô tả": "Loạt các cuộc cách mạng dẫn đến việc lật đổ chế độ Nga hoàng."
        }
    }
    query_lower = query_text.lower()
    for event, details in historical_events.items():
        if event in query_lower:
            response = f"Về {event.capitalize()}: "
            if "bắt đầu" in details and "kết thúc" in details:
                response += f"Bắt đầu vào {details['bắt đầu']} và kết thúc vào {details['kết thúc']}. "
            elif "ngày" in details:
                response += f"Diễn ra vào {details['ngày']}. "
            response += details["mô tả"]
            return response
    return None