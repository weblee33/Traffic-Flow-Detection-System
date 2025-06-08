import json, time, pathlib, cv2
from yt_dlp import YoutubeDL
from ultralytics import YOLO
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = "templates"
HTML_OUT     = pathlib.Path("docs/index.html")
# ── constants ───────────────────────────────────────────
# 這是 YouTube 上的車流量監測影片，使用 YOLOv8 模型偵測車輛數量。
URL     = "https://www.youtube.com/watch?v=pmM2CeSAx0I"
VEH_ID  = {2, 3, 5, 7}          # car/ moto/ bus/ truck
JSON_FN = pathlib.Path("data/vehicles.json")
HTML_FN = pathlib.Path("docs/index.html")

def resolve_stream(url: str) -> str:
    ydl_opts = {'format': 'best[ext=mp4][height<=720]', 'quiet': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info["url"] if "url" in info else info["requested_formats"][0]["url"]

def append_stat(ts, count):
    JSON_FN.parent.mkdir(exist_ok=True)
    try:
        data = json.loads(JSON_FN.read_text())
    except FileNotFoundError:
        data = []
    data.append({"t": ts, "c": count})
    JSON_FN.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    return data

def patch_html(latest):
    """把頁面 <span id="latest"> 改成目前壅塞等級文字。"""
    html = HTML_FN.read_text(encoding="utf-8")
    html = html.replace(
        "{{LATEST}}", latest)  # 簡單替換範例；可用 Jinja2
    HTML_FN.write_text(html, encoding="utf-8")

def main():
    stream_url = resolve_stream(URL)
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        raise RuntimeError("Cannot open stream")

    model = YOLO("weights/yolov8n.pt")
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("first frame failed")

    r = model(frame, verbose=False)[0]
    num_veh = sum(int(c) in VEH_ID for c in r.boxes.cls)
    level = "heavy" if num_veh >= 15 else "moderate" if num_veh >= 8 else "light"
    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    data = append_stat(ts, num_veh)
    render_html(level, ts, data)
    print(f"[{ts}] vehicles={num_veh} → {level}")

# ── render HTML ──────────────────────────────────────────
def render_html(level: str, ts: str, data: list):
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape()
    )
    tpl  = env.get_template("index.html")
    html = tpl.render(level=level, timestamp=ts, data=data)
    HTML_OUT.parent.mkdir(exist_ok=True)
    HTML_OUT.write_text(html, encoding="utf-8")

if __name__ == "__main__":
    main()
