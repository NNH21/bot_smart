from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from command_processor import process_command
import logging
import os
import time
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
TEMP_DIR = "temp_audio"
BEEP_SOUND = os.path.join(TEMP_DIR, "beep.wav")

# Tạo file âm thanh "beep" nếu chưa tồn tại
def create_beep_sound():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    if not os.path.exists(BEEP_SOUND):
        try:
            import numpy as np
            import wave
            sample_rate = 44100
            duration = 0.3
            frequency = 880
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            audio = 0.7 * np.sin(2 * np.pi * frequency * t)
            audio = (audio * 32767).astype(np.int16)
            with wave.open(BEEP_SOUND, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio.tobytes())
            logging.info(f"Đã tạo file âm thanh beep: {BEEP_SOUND}")
        except ImportError:
            logging.warning("Không thể tạo file âm thanh beep. Numpy hoặc wave không được cài đặt.")
        except Exception as e:
            logging.error(f"Lỗi khi tạo file âm thanh beep: {e}")

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
        # Sử dụng tham số slow để điều chỉnh tốc độ nói dựa trên SPEECH_RATE
        is_slow = SPEECH_RATE <= 0.8
        tts = gTTS(text=response, lang='vi', slow=is_slow)
        tts.save(audio_path)
        audio_url = f"/audio/{audio_filename}"
        logging.info(f"Đã tạo file âm thanh: {audio_path} với tốc độ {SPEECH_RATE}")
    except Exception as e:
        logging.error(f"Lỗi khi tạo file âm thanh: {e}")
        audio_url = None

    return jsonify({'response': response, 'audio_url': audio_url})

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
    logging.info("Starting Flask server on port 5000")
    create_beep_sound()
    app.run(debug=True, port=5000)