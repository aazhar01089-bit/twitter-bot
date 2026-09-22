import os
import http.server
import socketserver
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# --- 1. Dummy HTTP Server for Render Free Web Service ---
class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = socketserver.TCPServer(("", port), HealthCheckHandler)
    print(f"Dummy HTTP server running on port {port}")
    server.serve_forever()

# --- 2. Telegram Bot Handlers ---
BOT_TOKEN = "8662033885:AAFTN4pHTnfk_paO355XQBXcH2fJi5TZfAk"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل لي رابط فيديو من تويتر/X وسأقوم بتحميله لك.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "x.com" in url or "twitter.com" in url:
        msg = await update.message.reply_text("جاري تحميل الفيديو، انتظر لحظة...")
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloaded_video.mp4',
            'quiet': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('downloaded_video.mp4', 'rb') as video_file:
                await update.message.reply_video(video=video_file)
            
            os.remove('downloaded_video.mp4')
            await msg.delete()
        except Exception as e:
            await update.message.reply_text(f"حدث خطأ أثناء التحميل: {str(e)}")
    else:
        await update.message.reply_text("من فضلك أرسل رابط تويتر/X صحيح.")

# --- 3. Main Execution ---
if __name__ == '__main__':
    # Start web server in background thread
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    # Start Telegram Bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running...")
    app.run_polling()

