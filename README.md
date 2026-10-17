# AirScript
Its my first Project and Its AirScript

AirScript Pro is a real-time, AI-powered digital painting application. Using just your webcam and computer vision, it tracks your hand gestures in real-time to paint, erase, trigger burst particles, and control canvas states without touching your keyboard or mouse.

---

## ✨ Features
- **Real-Time Hand Tracking:** Powered by MediaPipe for low-latency finger and palm tracking.
- **Dynamic Gesture Recognition:** Seamlessly switch between drawing, erasing, and triggering effects with hand shapes.
- **Particle Physics Engine:** Custom text-based particle effects (`01ABCDEF`) that react to gravity and movement.
- **Dynamic HUD:** A clean, dark heads-up display showing active modes, colors, brush size, and a live color palette.
- **Rainbow Mode:** Cycle through a vibrant HSV color wheel while drawing.
- **Export Artwork:** Instantly save your canvas drawings directly to your machine.

---

## 🎮 Hand Gestures

| Gesture | Action | Description |
| :--- | :--- | :--- |
| **☝️ Index Finger Up** | `DRAW` | Standard painting mode or local eraser (depending on settings). |
| **🖐️ Open Palm** | `PALM` | Spawns a stream of digital particles tracking your palm. |
| **✌️ Index & Middle Up** | `BURST` | Triggers a massive explosion of floating particles. |
| **✊ Full Fist** | `ERASE` | Acts as a large circular local eraser tracking your hand. |

---

## ⌨️ Keyboard Shortcuts

Fine-tune your experience using your keyboard while the application is active:

*   **`1` to `8`** : Swap between preset colors (Green, Cyan, Blue, Purple, Pink, Orange, White, Yellow).
*   **`E`** : Toggle Eraser mode on/off for the index finger.
*   **`R`** : Toggle Rainbow drawing mode on/off.
*   **`+` / `-`** : Increase or decrease the brush thickness.
*   **`C`** : Clear the canvas completely.
*   **`S`** : Save your canvas drawing as a `.png` file.
*   **`Q`** : Quit the application safely.

---

## 🚀 Installation & Setup

### Prerequisites
- **Python:** Version `3.8`, `3.9`, `3.10`, or `3.11` is highly recommended.
- **Hardware:** A working internal or external USB webcam.

### Step-by-Step Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd airscript-pro
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 🛠️ Built With
- **OpenCV** - Image and video frame stream handling.
- **MediaPipe** - High-fidelity hand landmark detection.
- **NumPy** - High-performance canvas matrix rendering.
