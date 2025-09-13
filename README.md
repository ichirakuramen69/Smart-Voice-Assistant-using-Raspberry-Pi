# Smart-Voice-Assistant-using-Raspberry-Pi

A **Flask-based backend server** with **Socket.IO** integration for building a Voice Assistant Web Interface.  
This app provides a simple way to run your assistant logic (`beta.py`), view its terminal output in **real time**, and manage **recording files** through a web interface.

---

## 🚀 Features
- 🔗 **Flask web server** with HTML templates.
- ⚡ **Real-time terminal streaming** from `beta.py` using WebSockets.
- 📂 **Recordings API** to list and view transcripts (`recording_*.txt`).
- 🛠️ Organized project structure for easy scaling.
- 🐳 **Docker support** for simple deployment across platforms.

---

## 📂 Project Structure

├── app.py                 # Flask + Socket.IO backend
├── beta.py                # Voice assistant backend script
├── templates/             # HTML templates
├── static/                # Static files (CSS/JS)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation

---

## 🔧 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/voice-assistant-web.git
cd voice-assistant-web

2️⃣ Create a Virtual Environment

python3 -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows (PowerShell)

3️⃣ Install Dependencies

pip install -r requirements.txt


⸻

▶️ Running the Server

Run the backend locally:

python app.py

Expected output:

🌐 Starting Voice Assistant Web Interface
📁 Project Directory: /path/to/voice-assistant-web
🔗 Access at: http://localhost:5000

Then open http://localhost:5000 in your browser.

⸻

🐳 Docker Setup

You can also run this app in Docker, making it easy to share with your teammate or deploy anywhere.

Build the Docker Image

docker build -t voice-assistant:latest .

Run the Container

docker run -it --rm -p 5000:5000 voice-assistant:latest

Access at http://localhost:5000.

⸻

📡 API Endpoints

Endpoint	Method	Description
/api/recordings	GET	List all recordings with metadata
/api/recording/<filename>	GET	Fetch content of a specific recording

Example:

curl http://localhost:5000/api/recordings


⸻

⚡ WebSocket Events

Event	Direction	Description
start_terminal	Client → Server	Start streaming beta.py terminal output
stop_terminal	Client → Server	Stop streaming terminal output
terminal_output	Server → Client	Emitted when a new line of terminal output is available
terminal_status	Server → Client	Status updates (connected/disconnected)
terminal_error	Server → Client	Error messages from backend


⸻

🧩 Requirements
	•	Python 3.8+
	•	Flask 3.x
	•	Flask-SocketIO
	•	Eventlet
	•	(See requirements.txt for the full list.)

⸻

🖥️ Cross-Platform Notes
	•	macOS/Linux: Use the commands above.
	•	Windows: Activate virtual environment via:

venv\Scripts\activate

and run the same commands.

⸻

🤝 Contributing
	1.	Fork this repository.
	2.	Create your feature branch:

git checkout -b feature/my-feature


	3.	Commit your changes:

git commit -m 'Add new feature'


	4.	Push to your branch:

git push origin feature/my-feature


	5.	Open a Pull Request.

⸻

📜 License

This project is licensed under the MIT License. See LICENSE for details.

---

✅ You can copy this whole thing into your `README.md`.  
Would you also like me to **write a Dockerfile** that installs everything from `requirements.txt` so your teammate can just `docker pull` and run?
