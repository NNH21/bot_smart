from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from command_processor import process_command
import logging
import os
import time
import serial
import threading
from gtts import gTTS
from config import SPEECH_RATE
import pygame

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# Cấu hình CORS với các tùy chọn chi tiết hơn để đảm bảo hoạt động trên mọi domain
CORS(app, resources={r"/*": {"origins": "*", 
                             "methods": ["GET", "POST", "OPTIONS"],
                             "allow_headers": ["Content-Type", "Authorization", "Accept"]}})

# Thư mục lưu file âm thanh tạm thời
AUDIO_DIR = "audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Định nghĩa đường dẫn đến file âm thanh beep
BEEP_SOUND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio', 'beep.mp3')

# Biến để lưu kết nối serial
ser = None
serial_lock = threading.Lock()

# Kết nối với ESP8266 qua cổng serial
def connect_to_esp():
    global ser
    try:
        # Tìm cổng COM phù hợp - thử qua nhiều cổng phổ biến
        possible_ports = ['COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10', 'COM11', 'COM12']
        
        for port in possible_ports:
            try:
                # Thử mở cổng và đóng lại để kiểm tra
                test_ser = serial.Serial(port, 115200, timeout=1)
                test_ser.close()
                
                # Nếu không lỗi, mở lại kết nối và sử dụng
                ser = serial.Serial(port, 115200, timeout=1)
                time.sleep(2)  # Đợi ESP8266 khởi động lại sau khi kết nối Serial
                logging.info(f"Đã kết nối với ESP8266 qua cổng {port}")
                
                # Gửi lệnh kiểm tra
                with serial_lock:
                    test_command = "STATE:READY\n"
                    ser.write(test_command.encode())
                    time.sleep(0.5)
                    response = ser.readline().decode('utf-8', errors='ignore').strip()
                    if response:
                        logging.info(f"ESP8266 phản hồi: {response}")
                
                return True
            except Exception as e:
                logging.warning(f"Không thể kết nối với cổng {port}: {e}")
                continue
        
        logging.warning("Không thể kết nối với ESP8266 trên bất kỳ cổng nào")
        return False
    except Exception as e:
        logging.error(f"Lỗi tổng thể khi kết nối với ESP8266: {e}")
        return False

# Gửi trạng thái đến ESP8266
def send_state_to_esp(state):
    global ser
    if ser is None or not ser.is_open:
        if not connect_to_esp():
            logging.error("Không thể kết nối với ESP8266")
            return False
    
    try:
        with serial_lock:
            command = f"STATE:{state}\n"
            # Gửi lệnh và đảm bảo dữ liệu được ghi
            ser.write(command.encode())
            ser.flush()
            time.sleep(0.1)  # Đợi một chút để ESP8266 xử lý
            logging.info(f"Đã gửi trạng thái {state} đến ESP8266")
            
            # Đọc phản hồi để xác nhận ESP8266 đã nhận được lệnh
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                logging.info(f"ESP8266 phản hồi sau khi gửi trạng thái: {response}")
            
        return True
    except Exception as e:
        logging.error(f"Lỗi khi gửi trạng thái đến ESP8266: {e}")
        ser = None  # Đánh dấu mất kết nối
        return False

# Kiểm tra kết nối ESP8266 định kỳ
def check_esp_connection():
    global ser
    while True:
        if ser is None or not ser.is_open:
            connect_to_esp()
        time.sleep(30)  # Kiểm tra mỗi 30 giây

# Phát âm thanh beep
def play_beep():
    try:
        if os.path.exists(BEEP_SOUND):
            pygame.mixer.music.load(BEEP_SOUND)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            logging.info("Đã phát âm thanh beep")
        else:
            logging.warning(f"Không tìm thấy file âm thanh beep tại {BEEP_SOUND}")
    except Exception as e:
        logging.error(f"Lỗi khi phát âm thanh beep: {e}")

# Khởi tạo pygame cho âm thanh
pygame.mixer.init()

@app.route('/process', methods=['POST'])
def process():
    logging.info("Received request to /process endpoint")
    data = request.json
    logging.info(f"Request data: {data}")
    query = data.get('query', '')
    
    # Gửi trạng thái đang lắng nghe đến ESP8266
    send_state_to_esp("LISTENING")
    
    response = process_command(query)
    logging.info(f"Response: {response}")

    # Phát âm thanh beep trước khi tạo file âm thanh
    play_beep()

    # Chuyển phản hồi thành file âm thanh tiếng Việt bằng gTTS
    try:
        audio_filename = f"response_{int(time.time())}.mp3"
        # Use absolute path for audio directory
        audio_dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio')
        if not os.path.exists(audio_dir_path):
            os.makedirs(audio_dir_path)
        audio_path = os.path.join(audio_dir_path, audio_filename)
        # Sử dụng tham số slow=False để đảm bảo tốc độ nhanh hơn
        is_slow = False  # Luôn đặt là False để tăng tốc độ phản hồi
        tts = gTTS(text=response, lang='vi', slow=is_slow)
        tts.save(audio_path)
        audio_url = f"/audio/{audio_filename}"
        logging.info(f"Đã tạo file âm thanh: {audio_path} với tốc độ {SPEECH_RATE}")
        
        # Gửi trạng thái đã trả lời đến ESP8266
        send_state_to_esp("ANSWERED")
        
    except Exception as e:
        logging.error(f"Lỗi khi tạo file âm thanh: {e}")
        audio_url = None
        # Nếu không tạo được file âm thanh, vẫn phải gửi trạng thái đã trả lời
        send_state_to_esp("ANSWERED")
    
    return jsonify({'response': response, 'audio_url': audio_url})

@app.route('/update_lcd_state', methods=['POST'])
def update_lcd_state():
    data = request.json
    state = data.get('state')
    
    if state not in ["READY", "LISTENING", "ANSWERED"]:
        return jsonify({'success': False, 'message': 'Trạng thái không hợp lệ'}), 400
    
    success = send_state_to_esp(state)
    if success:
        return jsonify({'success': True, 'message': f'Đã cập nhật trạng thái LCD thành {state}'})
    else:
        return jsonify({'success': False, 'message': 'Không thể kết nối với ESP8266'}), 500

@app.route('/audio/<filename>', methods=['GET'])
def serve_audio(filename):
    # Use absolute path for audio files
    audio_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio', filename)
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mpeg')
    else:
        logging.error(f"File không tồn tại: {audio_path}")
        return jsonify({'error': 'File âm thanh không tồn tại.'}), 404

@app.route('/set_speech_rate', methods=['POST'])
def set_speech_rate():
    global SPEECH_RATE
    data = request.json
    new_rate = data.get('rate')
    if new_rate is not None:
        try:
            new_rate = float(new_rate)
            if 0.4 <= new_rate <= 1.8:
                SPEECH_RATE = new_rate
                return jsonify({'success': True, 'message': f'Đã đặt tốc độ nói thành {SPEECH_RATE}', 'rate': SPEECH_RATE})
            else:
                return jsonify({'success': False, 'message': 'Tốc độ nói phải nằm trong khoảng 0.4 đến 1.8'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Giá trị tốc độ không hợp lệ'}), 400
    return jsonify({'success': False, 'message': 'Không có giá trị tốc độ được cung cấp'}), 400

@app.route('/get_speech_rate', methods=['GET'])
def get_speech_rate():
    return jsonify({'rate': SPEECH_RATE})

if __name__ == "__main__":
    # Thử kết nối với ESP8266 khi khởi động
    connect_to_esp()
    
    # Bắt đầu thread kiểm tra kết nối ESP8266 định kỳ
    check_thread = threading.Thread(target=check_esp_connection, daemon=True)
    check_thread.start()
    
    # Gửi trạng thái sẵn sàng ban đầu
    send_state_to_esp("READY")
    
    logging.info("Starting Flask server on port 5000")
    app.run(debug=True, port=5000)