# Line Bot 媒體檔案自動備份到 Dropbox

這是一個 Line Bot 應用程式，可以自動將 Line 群組中的照片儲存到 Dropbox。

## 功能

* 自動儲存群組內的照片
* 使用時間戳記確保檔案名稱唯一性
* 支援 Zeabur 部署

## 本地開發

### 安裝需求

1. Python 3.9+
2. pip（Python 套件管理器）

### 安裝步驟

1. 安裝相依套件：
```bash
pip install -r requirements.txt
```

2. 設定環境變數：
   * 複製 `.env.example` 到 `.env`
   * 使用您的 API 金鑰
   * ⚠️ 注意：不要將含有真實 API 金鑰的 `.env` 檔案提交到 Git

3. 執行應用程式：
```bash
python app.py
```

## Zeabur 部署步驟

1. 在 Zeabur 建立新專案
2. 連接 GitHub 儲存庫
3. 設定環境變數：
   - `LINE_CHANNEL_SECRET`
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `DROPBOX_APP_KEY`
   - `DROPBOX_APP_SECRET`
   - `DROPBOX_REFRESH_TOKEN`
4. 部署應用程式
5. 在 Line Developer Console 設定 Webhook URL：`https://<your-zeabur-domain>/callback`

## 注意事項

1. 確保已在 Line Developer Console 開啟 Webhook
2. 確保 Dropbox API 設定正確
3. 建議定期檢查 Dropbox 空間使用量
4. ⚠️ 安全性提醒：
   - 永遠不要在程式碼中硬編碼 API 金鑰
   - 確保 `.env` 檔案已加入 `.gitignore`
   - 定期更新 API 金鑰
   - 在 Zeabur 中安全地設定環境變數 