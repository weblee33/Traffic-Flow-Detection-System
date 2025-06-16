import os, time, json, pathlib, cv2
from datetime import datetime, timedelta, timezone
from ultralytics import YOLO
from jinja2 import Environment, FileSystemLoader, select_autoescape
from yt_dlp import YoutubeDL

# === 設定參數 ===
YOUTUBE_URL = "https://www.youtube.com/watch?v=pmM2CeSAx0I"
COOKIE_FILE = "detector/youtube_cookies_taiwan.txt"
YOLO_MODEL  = "weights/yolov8n.pt"
JSON_PATH   = pathlib.Path("docs/data/vehicles.json")
HTML_PATH   = pathlib.Path("docs/index.html")
TEMPLATE_DIR = "templates"
SNAPSHOT_PATH = pathlib.Path("docs/snapshot.jpg")
VEHICLE_IDS = {2, 3, 5, 7}  # car, motorcycle, bus, truck

# 台灣時區 UTC+8
tz_taiwan = timezone(timedelta(hours=8))

# 取得直播串流的影片 URL
def get_stream_url(url, cookie_file=None):
    ydl_opts = {'format': 'best[ext=mp4][height<=720]', 'quiet': True}
    if cookie_file and os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("url") or info["requested_formats"][0]["url"]

# 根據偵測到的車輛數分類交通程度
def classify(count):
    if count >= 15: return "heavy"
    elif count >= 8: return "moderate"
    else: return "light"

# 寫入車流紀錄 JSON（每 5 分鐘才寫一次）
def append_record(ts, count):
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except:
        data = []

    now_ts = datetime.fromisoformat(ts)

    if data:
        last_ts = datetime.fromisoformat(data[-1]["t"])
        # 若無時區，補上台灣時區
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=tz_taiwan)

        # 小於 5 分鐘不記錄
        if (now_ts - last_ts).total_seconds() < 300:
            return data

    data.append({"t": ts, "c": count})
    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data

# 使用 Jinja2 模板渲染 HTML
def render_html(level, timestamp, data, snapshot_filename):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape())
    tpl = env.get_template("index.html")
    html = tpl.render(level=level, timestamp=timestamp, data=data, snapshot=snapshot_filename)
    HTML_PATH.write_text(html, encoding="utf-8")

# 主程式
def main():
    print("🚦 Traffic detection demo started (every 60 sec)")
    model = YOLO(YOLO_MODEL)
    stream_url = get_stream_url(YOUTUBE_URL, COOKIE_FILE)
    cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        raise RuntimeError("❌ 無法開啟影片串流")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("⚠️ 無法讀取影像，等待重試...")
            time.sleep(2)
            continue

        result = model(frame, verbose=False)[0]
        count = sum(int(c) in VEHICLE_IDS for c in result.boxes.cls)
        level = classify(count)
        ts = datetime.now(tz=tz_taiwan).isoformat()  # 使用台灣時間，含時區

        # 儲存偵測畫面截圖
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(SNAPSHOT_PATH), frame)

        # 更新資料與網頁
        data = append_record(ts, count)
        render_html(level, ts, data, snapshot_filename=SNAPSHOT_PATH.name)

        print(f"[{ts}] 🚗 vehicles={count} → {level}")
        time.sleep(60)  # 每分鐘偵測一次

if __name__ == "__main__":
    main()

# 網頁預覽：http://localhost:8000/docs/index.html
