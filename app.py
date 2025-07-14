from flask import Flask, request, send_file, render_template
import yt_dlp
import os
import re

app = Flask(__name__)

# 📁 مجلد التحميلات المؤقت
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 🧼 دالة لتنظيف الاسم ديال الفيديو
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_audio():
    url = request.form.get('url')
    if not url:
        return "❌ لا يوجد رابط", 400

    # نجيبو عنوان الفيديو أولاً
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'no_title'))
    except Exception as e:
        return f"❌ خطأ فـ استخراج العنوان: {e}", 500

    # نحطو مسار الملف النهائي
    output_path = os.path.join(DOWNLOAD_DIR, f"{title}.mp3")

    # ⚙️ إعدادات yt_dlp لتحويل الصوت إلى mp3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path.replace(".mp3", ".%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
        'socket_timeout': 30,
        'nocheckcertificate': True,
        'ffmpeg_location': r'C:\Users\badre\Desktop\ffmpeg-release-full\bin'  # ✅ تأكد من المسار الصحيح
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return f"❌ فشل التحميل: {e}", 500

    # 📥 نرسل الملف مباشرة للتحميل
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
