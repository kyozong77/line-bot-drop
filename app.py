from flask import Flask, request, abort, jsonify
import os
from dotenv import load_dotenv
import dropbox
from dropbox.files import WriteMode, CreateFolderError
from dropbox.exceptions import ApiError
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)

load_dotenv()

app = Flask(__name__)

# LINE Bot configuration
configuration = Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
)
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# Dropbox configuration
dbx = dropbox.Dropbox(
    oauth2_refresh_token=os.getenv('DROPBOX_REFRESH_TOKEN'),
    app_key=os.getenv('DROPBOX_APP_KEY'),
    app_secret=os.getenv('DROPBOX_APP_SECRET')
)

DROPBOX_FOLDER = '/家庭相簿'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        abort(400, description='X-Line-Signature header is missing')

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400, description='Invalid signature')
    except Exception as e:
        app.logger.error(f"Webhook handling error: {e}")
        abort(500, description='Internal server error')

    return 'OK'

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    """處理圖片訊息"""
    try:
        message_content = download_line_content(event.message.id)
        if message_content:
            filename = f"{event.message.id}_{int(event.timestamp/1000)}.jpg"
            if save_to_dropbox(message_content, filename):
                with ApiClient(configuration) as api_client:
                    line_bot_api = MessagingApi(api_client)
                    line_bot_api.reply_message_with_http_info(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="圖片已儲存到 Dropbox")]
                        )
                    )
    except Exception as e:
        app.logger.error(f"Error handling image: {e}")

def download_line_content(message_id):
    """下載 LINE 訊息內容"""
    try:
        with ApiClient(configuration) as api_client:
            messaging_api = MessagingApi(api_client)
            stream = messaging_api.get_message_content_by_id(message_id)
            content = stream.content
            if hasattr(content, 'read'):
                return content.read()
            return content
    except Exception as e:
        app.logger.error(f"Error downloading content: {e}")
        return None

def save_to_dropbox(image_content, filename):
    """儲存圖片到 Dropbox"""
    try:
        try:
            dbx.files_create_folder_v2(DROPBOX_FOLDER)
        except ApiError as e:
            if not isinstance(e.error, CreateFolderError) or \
               not e.error.is_path() or \
               not e.error.get_path().is_conflict():
                raise
        
        file_path = f"{DROPBOX_FOLDER}/{filename}"
        dbx.files_upload(
            image_content,
            file_path,
            mode=WriteMode('overwrite')
        )
        return True
    except ApiError as e:
        app.logger.error(f"Dropbox API error: {e}")
        return False

@app.route("/", methods=['GET'])
def home():
    return jsonify({
        "status": "running",
        "message": "LINE Bot is running!"
    })

@app.route("/health", methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "OK"
    })

if __name__ == "__main__":
    app.run() 