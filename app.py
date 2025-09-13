#!/usr/bin/env python3
"""
Flask backend server for Voice Assistant Web Interface
Handles file access, terminal streaming, and API endpoints
"""

from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import os
import glob
import subprocess
import threading
import time
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = PROJECT_DIR  # Recordings are in the same directory as beta.py
BETA_SCRIPT = os.path.join(PROJECT_DIR, 'beta.py')

# Global variables for terminal streaming
terminal_process = None
streaming_active = False

class TerminalStreamer:
    def __init__(self):
        self.process = None
        self.thread = None
        self.active = False
    
    def start_streaming(self):
        if self.active:
            return
        
        self.active = True
        self.thread = threading.Thread(target=self._stream_output)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_streaming(self):
        self.active = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
    
    def _stream_output(self):
        try:
            # Start the beta.py process
            self.process = subprocess.Popen(
                ['python3', BETA_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            socketio.emit('terminal_status', {'status': 'connected', 'message': 'Connected to beta.py terminal'})
            
            # Stream output line by line
            while self.active and self.process and self.process.poll() is None:
                try:
                    line = self.process.stdout.readline()
                    if line:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        socketio.emit('terminal_output', {
                            'timestamp': timestamp,
                            'output': line.strip()
                        })
                    else:
                        time.sleep(0.1)
                except Exception as e:
                    socketio.emit('terminal_error', {'error': str(e)})
                    break
        
        except Exception as e:
            socketio.emit('terminal_error', {'error': f'Failed to start beta.py: {str(e)}'})
        
        finally:
            self.active = False
            if self.process:
                try:
                    self.process.terminate()
                except:
                    pass
            socketio.emit('terminal_status', {'status': 'disconnected', 'message': 'Terminal disconnected'})

# Global terminal streamer instance
terminal_streamer = TerminalStreamer()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/recordings')
def recordings():
    return render_template('recordings.html')

@app.route('/terminal')
def terminal():
    return render_template('terminal.html')

@app.route('/api/recordings')
def get_recordings():
    """Get list of all recording files"""
    try:
        pattern = os.path.join(RECORDINGS_DIR, 'recording_*.txt')
        files = glob.glob(pattern)
        
        recordings = []
        for file_path in files:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            modified_time = os.path.getmtime(file_path)
            
            recordings.append({
                'filename': file_name,
                'size': file_size,
                'modified': datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S'),
                'path': file_name
            })
        
        # Sort by modification time (newest first)
        recordings.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'recordings': recordings,
            'count': len(recordings)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recording/<filename>')
def get_recording_content(filename):
    """Get content of a specific recording file"""
    try:
        # Security check - only allow .txt files starting with 'recording_'
        if not filename.startswith('recording_') or not filename.endswith('.txt'):
            return jsonify({'success': False, 'error': 'Invalid filename'}), 400
        
        file_path = os.path.join(RECORDINGS_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content': content,
            'line_count': len(content.split('\n')) if content else 0
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Socket.IO events for terminal streaming
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('terminal_status', {'status': 'ready', 'message': 'WebSocket connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_terminal')
def handle_start_terminal():
    """Start streaming terminal output"""
    terminal_streamer.start_streaming()

@socketio.on('stop_terminal')
def handle_stop_terminal():
    """Stop streaming terminal output"""
    terminal_streamer.stop_streaming()

if __name__ == '__main__':
    # Ensure templates and static directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print(f"🌐 Starting Voice Assistant Web Interface")
    print(f"📁 Project Directory: {PROJECT_DIR}")
    print(f"📄 Beta Script: {BETA_SCRIPT}")
    print(f"🎙️ Recordings Directory: {RECORDINGS_DIR}")
    print(f"🔗 Access at: http://localhost:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)