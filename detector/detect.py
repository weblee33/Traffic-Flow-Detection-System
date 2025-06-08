"""
detect.py  ─ Traffic-Flow-Detection-System
-------------------------------------------------
  1. 解析 YouTube 直播串流（支援 480p~720p）
  2. 每次執行抓 1 張影像 → YOLOv8 只統計車輛
  3. 先將攝影機當地時間 (Fresno, US) 轉成台灣時間後
     寫入 data/vehicles.json
  4. 用 Jinja2 重新產生 docs/index.html（含互動折線圖）
"""

import json, time, pathlib, cv2
from datetime import datetime
from zoneinfo import ZoneInfo            # Python 3.9+ 內建
from yt_dlp import YoutubeDL
from ultralytics import YOLO
from jinja2 import Environment, FileSystemLoader, select_autoescape
import numpy as np                       # 只為過濾 boxes 用

# ───────────── 常數與路徑 ──────────────────────────
YOUTUBE_URL = "https://www.youtube.com/watch?v=qMYlpMsWsBE"  # Fresno 直播
COOKIE_FILE = None                       # 若需登入請填 "youtube_cookies.txt"

VEHICLE_IDS = {2, 3, 5, 7}               # COCO: car、motorcycle、bus、truck
JSON_PATH   = pathlib.Path("data/vehicles.json")
HTML_PATH   = pathlib.Path("docs/index.html")
TEMPLATE_DIR = pathlib.Path("templates")

CAM_TZ = ZoneInfo("America/Los_Angeles")  # Fresno 所在時區


# ───────────── 取得 YouTube 串流 URL ───────────────
def get_stream_url(url: str, cookies: str | None = None) -> str:
    ydl_opts = {
        "format": "best[ext=mp4][height<=480]",  # 限 480p 省頻寬更穩
        "quiet":  True
    }
    if cookies:
        ydl_opts["cookiefile"] = cookies
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["url"]

# ───────────── 寫入 JSON ───────────────────────────
def append_record(ts_tw: str, count: int) -> list:
    JSON_PATH.parent.mkdir(exist_ok=True)
    try:
        data = json.loads(JSON_PATH.read_text())
    except FileNotFoundError:
        data = []
    data.append({"t": ts_tw, "c": count})
    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return data

# ───────────── 產生 / 更新 HTML ────────────────────
def render_html(level:str, ts_tw:str, data:list):
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape()
    )
    html = env.get_template("index.html").render(
        level=level,
        timestamp=ts_tw,
        data=data
    )
    HTML_PATH.parent.mkdir(exist_ok=True)
    HTML_PATH.write_text(html, encoding="utf-8")

# ───────────── 主程式 ──────────────────────────────
def main():
    # 1) 解析 YouTube 串流
    stream = get_stream_url(YOUTUBE_URL, COOKIE_FILE)
    cap = cv2.VideoCapture(stream)
    if not cap.isOpened():
        raise RuntimeError("🚫 無法開啟 YouTube 串流，檢查影片或 Cookie")

    # 2) 抓第一張影像
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError("🚫 讀取影像失敗")

    # 3) YOLOv8 偵測 + 只保留車輛
    model  = YOLO("weights/yolov8n.pt")
    result = model(frame, verbose=False)[0]
    mask   = np.array([int(c) in VEHICLE_IDS for c in result.boxes.cls])
    result.boxes = result.boxes[mask]
    vehicle_cnt  = len(result.boxes)

    level = ("heavy" if vehicle_cnt >= 15 else
             "moderate" if vehicle_cnt >= 8 else
             "light")

    # 4) 取得時間：攝影機當地 → 台灣
    dt_cam = datetime.now(tz=CAM_TZ)
    ts_cam = dt_cam.strftime("%Y-%m-%d %H:%M:%S")

    # 5) 保存 JSON 並更新 HTML
    data = append_record(ts_cam, vehicle_cnt)
    render_html(level, ts_cam, data)

    print(f"[CAM {ts_cam}] vehicles={vehicle_cnt:2d} → {level}")
    # 若要本機即時預覽可取消下一行註解
    # cv2.imshow("Detection", result.plot()); cv2.waitKey(0); cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
