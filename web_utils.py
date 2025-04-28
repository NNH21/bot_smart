import urllib.parse
import webbrowser
import logging
import requests
from config import session

def open_youtube_video(query):
    try:
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        webbrowser.open(search_url)
        logging.info(f"Đã mở trang tìm kiếm YouTube cho: {query}")
        return True
    except Exception as e:
        logging.error(f"Lỗi khi mở YouTube: {e}")
        return False

def open_web_search(query):
    try:
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        try:
            webbrowser.get(chrome_path).open(search_url)
        except:
            webbrowser.open(search_url)
        logging.info(f"Đã mở trình duyệt để tìm kiếm: {query}")
        return True
    except Exception as e:
        logging.error(f"Lỗi khi mở trình duyệt: {e}")
        return False

def open_website(site):
    site_mapping = {
        "facebook": "https://www.facebook.com",
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "tiktok": "https://www.tiktok.com",
        "instagram": "https://www.instagram.com",
        "twitter": "https://www.twitter.com",
        "x": "https://www.twitter.com",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chat.openai.com",
        "grok": "https://grok.x.com",
        "github": "https://www.github.com",
        "tiki": "https://tiki.vn",
        "shopee": "https://shopee.vn",
        "lazada": "https://www.lazada.vn",
        "vnexpress": "https://vnexpress.net",
        "thanh niên": "https://thanhnien.vn",
        "tuổi trẻ": "https://tuoitre.vn",
        "zing": "https://zingnews.vn",
        "zing mp3": "https://zingmp3.vn",
        "zingmp3": "https://zingmp3.vn",
        "google drive": "https://drive.google.com",
        "google maps": "https://maps.google.com",
        "bản đồ": "https://maps.google.com",
    }
    try:
        site_clean = " ".join(site.lower().strip().split())
        url = None
        for key, value in site_mapping.items():
            if key == site_clean:
                url = value
                break
        if not url:
            site_domain = site_clean.replace(" ", "")
            url = f"https://{site_domain}"
            try:
                response = session.head(url, timeout=5, allow_redirects=True)
                if response.status_code >= 400:
                    url = f"https://www.{site_domain}.com"
                    response = session.head(url, timeout=5, allow_redirects=True)
                    if response.status_code >= 400:
                        search_query = urllib.parse.quote(site_clean)
                        url = f"https://www.google.com/search?q={search_query}"
            except requests.RequestException:
                search_query = urllib.parse.quote(site_clean)
                url = f"https://www.google.com/search?q={search_query}"

        chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'
        try:
            webbrowser.get(chrome_path).open(url)
        except:
            webbrowser.open(url)
        return f"Đã mở trang {site}"
    except Exception as e:
        logging.error(f"Lỗi khi mở website: {e}")
        return f"Không thể mở trang {site}. Vui lòng kiểm tra kết nối mạng hoặc tên trang web."