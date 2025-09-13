# Voice Assistant Web Interface

A comprehensive web-based interface for managing and monitoring voice assistant recordings with real-time terminal streaming capabilities.

## 🌟 Features

- **Real-time Terminal Streaming**: Monitor your voice assistant (`beta.py`) output in real-time through WebSocket connections
- **Recording Management**: Browse, view, and manage voice recording files with a clean web interface
- **File Browser**: Easy access to all recording files with metadata (size, modification time)
- **Live Terminal Control**: Start/stop terminal streaming with interactive controls
- **Responsive Design**: Modern web interface that works across devices
- **RESTful API**: Clean API endpoints for programmatic access to recordings and system status

## 🏗️ Architecture

The project consists of:
- **Flask Backend**: Serves the web interface and provides API endpoints
- **Socket.IO Integration**: Real-time bidirectional communication for terminal streaming
- **File Management System**: Secure access to recording files
- **Terminal Streamer**: Manages subprocess execution and output streaming

## 📋 Prerequisites

- Python 3.7 or higher
- Flask and Flask-SocketIO
- A `beta.py` script in the same directory (your voice assistant main script)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ichirakuramen69/Smart-Voice-Assistant-using-Raspberry-Pi.git
cd Smart-Voice-Assistant-using-Raspberry-Pi
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Ensure Your Voice Assistant Script

Make sure you have a `app.py` file in the same directory as the main Flask application. This should be your voice assistant main script.

## 🎯 Usage

### Starting the Server

```bash
python3 app.py
```

The server will start on `http://localhost:5000` and display:
- Project directory information
- Recordings directory path
- Access URL

### Accessing the Interface

Open your web browser and navigate to:
- **Main Interface**: `http://localhost:5000`
- **About Page**: `http://localhost:5000/about`
- **Recordings Manager**: `http://localhost:5000/recordings`
- **Terminal Monitor**: `http://localhost:5000/terminal`

## 📁 Directory Structure

```
voice-assistant-web-interface/
├── app.py                
├── beta.py              
├── requirements.txt       
├── templates/           
│   ├── index.html
│   ├── about.html
│   ├── recordings.html
│   └── terminal.html
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🎉 Acknowledgments

- Built with Flask and Socket.IO
- Inspired by modern web development practices
- Designed for voice assistant integration and monitoring
