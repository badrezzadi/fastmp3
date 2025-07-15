from flask import Flask, request, send_file, render_template
import yt_dlp
import os
import re

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'no_title'))
    except Exception as e:
        return f"❌ خطأ فـ استخراج العنوان: {e}", 500

    output_path = os.path.join(DOWNLOAD_DIR, f"{title}.mp3")

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
        'nocheckcertificate': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return f"❌ فشل التحميل: {e}", 500

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    # خاص بـ Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
