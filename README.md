# Traffic Flow Detection System

A real-time traffic monitoring and visualization system built with YOLOv8 and YouTube livestreams. This project detects vehicle density from public traffic camera feeds and presents the data on a visually rich, auto-updating dashboard hosted via GitHub Pages.

This system is designed for public awareness, research, or smart city integration and showcases an end-to-end pipeline from object detection to automated web deployment.

---

## 🚀 Features

* 🔍 **Real-time object detection** using YOLOv8 (Ultralytics) to recognize vehicle types (car, motorcycle, bus, truck)
* 📺 **YouTube livestream support** via `yt-dlp`, with optional cookie authentication
* 🌐 **Time zone conversion** — vehicle counts are recorded in camera-local time (e.g., America/Los\_Angeles)
* 📈 **Traffic congestion level classification** based on vehicle count (light / moderate / heavy)
* 📊 **Interactive charts** rendered with Chart.js, including:

  * Daily traffic trend
  * Rolling 3-hour traffic graph
* 💻 **Bootstrap-based responsive layout** with dark/light mode toggle
* 🔁 **Automated pipeline** every 5 minutes via GitHub Actions:

  * Video capture → YOLO detection → JSON update → HTML regeneration → commit & deploy
* 🌍 **Frontend hosted on GitHub Pages**, publicly accessible and continuously updated

---

## 🛠️ Tech Stack

| Layer                | Tools & Libraries                     |
| -------------------- | ------------------------------------- |
| **Object Detection** | YOLOv8 (Ultralytics), OpenCV          |
| **Video Stream**     | yt-dlp (for livestream video capture) |
| **Time Handling**    | `zoneinfo` (PEP-615, Python 3.9+)     |
| **Templating**       | Jinja2                                |
| **Visualization**    | Chart.js 4, Bootstrap 5               |
| **Scheduling**       | GitHub Actions (CRON trigger)         |
| **Deployment**       | GitHub Pages (static hosting)         |

---

## 📁 Project Structure

```
Traffic-Flow-Detection-System/
├── detector/                      # Detection pipeline
│   └── detect.py                  # Main script (YOLO + timestamp + render)
├── templates/                    # HTML template for Jinja2
│   └── index.html
├── docs/                         # Public website output
│   ├── index.html                # Dashboard (generated)
│   └── data/vehicles.json        # Traffic stats (auto-updated)
├── .github/workflows/            # Automation config
│   └── traffic.yml
├── weights/                      # YOLOv8 weights
│   └── yolov8n.pt                # Lightweight model
└── requirements.txt              # Python dependencies
```

---

## 📊 Traffic Congestion Levels

Traffic levels are classified in real-time according to the number of vehicles detected per frame:

| Level      | Condition     |
| ---------- | ------------- |
| `light`    | < 8 vehicles  |
| `moderate` | 8–14 vehicles |
| `heavy`    | ≥ 15 vehicles |

> You can adjust these thresholds in `detect.py` by modifying the logic around `vehicle_cnt`.

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/Traffic-Flow-Detection-System.git
cd Traffic-Flow-Detection-System
```

### 2. (Optional) Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Python dependencies

```bash
pip install -r detector/requirements.txt
```

### 4. Run detection locally

```bash
python detector/detect.py
```

> Captures a snapshot from YouTube livestream, detects vehicle count, appends to JSON, and renders the dashboard.

### 5. Preview dashboard

```bash
python -m http.server
# Then open browser at: http://localhost:8000/docs/index.html
```

---

## 🔄 GitHub Actions: Auto-Detection & Deployment

This project includes a GitHub Actions workflow (`traffic.yml`) which runs every 5 minutes and:

* Resolves the YouTube video stream
* Applies YOLOv8 detection
* Records vehicle count in `docs/data/vehicles.json`
* Regenerates `docs/index.html` with updated values
* Commits and pushes if changes are detected

> Tip: You can manually trigger the workflow using `workflow_dispatch` in the Actions tab.

Make sure the YOLO model file (`yolov8n.pt`) is under 100 MB or cached properly using GitHub Actions cache.

---

## 🌐 Live Demo

This project is publicly hosted and continuously updated at:

```
https://weblee33.github.io/Traffic-Flow-Detection-System/
```

https\://<your-username>.github.io/Traffic-Flow-Detection-System/

```

Ensure your repo settings → Pages → Source is set to the `docs/` folder.

---

## 📌 Potential Enhancements
- [ ] Add 7-day / 30-day traffic trend view
- [ ] Alert webhook integration for high congestion (e.g., LINE Notify)
- [ ] Downloadable CSV summary export for researchers
- [ ] Responsive filtering: camera selector, timeframe selector
- [ ] Add multi-camera support in `vehicles.json`

---

## ✍️ Author
**Winston (weblee33)**  
Senior student at National Chung Hsing University, Taiwan  
Focus areas: computer vision, AI, automation, cloud deployment

---

## 📄 License
[MIT License](LICENSE)

This project is open-source. Contributions, forks, and feature suggestions are welcome!

```
