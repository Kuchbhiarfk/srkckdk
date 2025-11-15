import time
import requests
import random
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib.parse import parse_qs, urlparse
from pymongo import MongoClient
import os
from datetime import datetime, timedelta
import json
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://your-connection-string")
DB_NAME = "Cluster0"
COLLECTION_NAME = "servers"
STATS_COLLECTION = "statistics"

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    stats_collection = db[STATS_COLLECTION]
    
    logger.info("✅ Connected to MongoDB")
except Exception as e:
    logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
    raise

# Global variables
APP_URL = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8000")
START_TIME = time.time()

# Fake user-agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.65 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "UptimeRobot/2.0 (http://uptimerobot.com/)",
]

# ==================== ULTIMATE KEEP-ALIVE SYSTEM ====================

class SelfPinger:
    """Self-ping to keep Render app alive"""
    def __init__(self, app_url, interval=0.1):
        self.app_url = app_url
        self.interval = interval
        self.is_running = False
        self.ping_count = 0
    
    def start(self):
        self.is_running = True
        thread = threading.Thread(target=self._ping_loop, daemon=True)
        thread.start()
        logger.info("🔄 Self-Ping System Started")
    
    def _ping_loop(self):
        while self.is_running:
            try:
                response = requests.get(
                    f"{self.app_url}/heartbeat",
                    timeout=10,
                    headers={"User-Agent": "SelfPinger/1.0"}
                )
                self.ping_count += 1
                logger.info(f"💓 Self-Ping #{self.ping_count}: {response.status_code}")
                
                # Update stats
                stats_collection.update_one(
                    {"type": "self_ping"},
                    {
                        "$set": {"last_ping": datetime.now()},
                        "$inc": {"count": 1}
                    },
                    upsert=True
                )
            except Exception as e:
                logger.error(f"❌ Self-Ping Failed: {e}")
            
            time.sleep(self.interval)


class ActivitySimulator:
    """Simulate activity to prevent sleep"""
    def __init__(self):
        self.activities = [
            self._db_query,
            self._memory_check,
            self._file_activity,
        ]
        self.is_running = False
    
    def start(self):
        self.is_running = True
        thread = threading.Thread(target=self._activity_loop, daemon=True)
        thread.start()
        logger.info("🎮 Activity Simulator Started")
    
    def _activity_loop(self):
        while self.is_running:
            try:
                activity = random.choice(self.activities)
                activity()
                time.sleep(random.randint(0.0001, 0.0002))  # 3-5 minutes
            except Exception as e:
                logger.error(f"Activity error: {e}")
    
    def _db_query(self):
        """Database keepalive query"""
        collection.find_one({"name": {"$exists": True}})
        logger.info("💾 DB Keepalive Query")
    
    def _memory_check(self):
        """Memory usage check"""
        memory = psutil.virtual_memory().percent
        logger.info(f"🧠 Memory Usage: {memory}%")
    
    def _file_activity(self):
        """File system activity"""
        with open('/tmp/keepalive.txt', 'w') as f:
            f.write(str(time.time()))
        logger.info("📁 File Activity")


class SleepPrevention:
    """Prevent Render from sleeping"""
    def __init__(self):
        self.last_activity = time.time()
        self.sleep_threshold = 10  # 14 minutes
        self.is_running = False
    
    def start(self):
        self.is_running = True
        thread = threading.Thread(target=self._monitor, daemon=True)
        thread.start()
        logger.info("😴 Sleep Prevention Started")
    
    def _monitor(self):
        while self.is_running:
            idle_time = time.time() - self.last_activity
            
            if idle_time >= self.sleep_threshold:
                logger.warning(f"⚠️ Idle for {int(idle_time)}s - Generating Activity!")
                self._generate_activity()
            
            time.sleep(0.0001)  # Check every minute
    
    def _generate_activity(self):
        try:
            requests.get("http://localhost:8000/heartbeat", timeout=2)
            self.update_activity()
            logger.info("✅ Activity Generated - Sleep Prevented")
        except:
            pass
    
    def update_activity(self):
        self.last_activity = time.time()


class UltimateKeepAlive:
    """Main Keep-Alive orchestrator"""
    def __init__(self, app_url):
        self.app_url = app_url
        self.components = []
        
    def setup(self):
        logger.info("🚀 Initializing Ultimate Keep-Alive System...")
        
        # Add components
        self.self_pinger = SelfPinger(self.app_url, interval=240)
        self.activity_sim = ActivitySimulator()
        self.sleep_prev = SleepPrevention()
        
        # Start all components
        self.self_pinger.start()
        self.activity_sim.start()
        self.sleep_prev.start()
        
        logger.info("✅ Ultimate Keep-Alive System Activated!")
        logger.info(f"📍 App URL: {self.app_url}")
        logger.info(f"⏱️  Self-Ping Interval: 1 Second")
        logger.info(f"🎯 Sleep Threshold: 10 Seconds")

# ==================== PING & MONITORING ====================

def ping_server(name, url, email=None, password=None):
    """Ping a server and log the result."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=20)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        # Update status in database
        collection.update_one(
            {"name": name},
            {
                "$set": {
                    "last_ping": datetime.now(),
                    "status": "online",
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "error": None,
                    "consecutive_failures": 0
                },
                "$inc": {"total_pings": 1, "successful_pings": 1}
            }
        )
        logger.info(f"✅ {name} ({url}) - Status: {response.status_code} - Time: {response_time}ms")
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        
        collection.update_one(
            {"name": name},
            {
                "$set": {
                    "last_ping": datetime.now(),
                    "status": "offline",
                    "error": error_msg,
                    "response_time": 0
                },
                "$inc": {
                    "total_pings": 1, 
                    "failed_pings": 1,
                    "consecutive_failures": 1
                }
            }
        )
        logger.error(f"❌ {name} ({url}) - Failed: {error_msg}")


def run_pings():
    """Run the ping loop indefinitely."""
    while True:
        logger.info("🔄 === Pinging All Servers ===")
        servers = list(collection.find())
        
        if len(servers) == 0:
            logger.info("📭 No servers to ping")
        else:
            for server in servers:
                ping_server(
                    server['name'], 
                    server['url'],
                    server.get('email'),
                    server.get('password')
                )
        
        logger.info("✅ === Ping Round Complete. Sleeping 5 minutes ===")
        time.sleep(0.00001)  # 5 minutes


def calculate_uptime(server):
    """Calculate uptime percentage"""
    total = server.get('total_pings', 0)
    successful = server.get('successful_pings', 0)
    
    if total == 0:
        return 0
    
    return round((successful / total) * 100, 2)


# ==================== HTTP SERVER ====================

class MonitorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default logging
    
    def do_GET(self):
        # Update sleep prevention
        keep_alive.sleep_prev.update_activity()
        
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.get_main_page().encode())
        
        elif self.path == "/heartbeat":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"alive")
        
        elif self.path == "/api/servers":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            servers = list(collection.find({}, {"_id": 0}))
            self.wfile.write(json.dumps(servers, default=str).encode())
        
        elif self.path == "/api/stats":
            uptime = time.time() - START_TIME
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            stats = {
                "app_uptime": int(uptime),
                "app_uptime_formatted": str(timedelta(seconds=int(uptime))),
                "memory_usage": psutil.virtual_memory().percent,
                "cpu_usage": psutil.cpu_percent(),
                "active_threads": threading.active_count(),
                "self_pings": keep_alive.self_pinger.ping_count,
            }
            
            self.wfile.write(json.dumps(stats).encode())
        
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        # Update sleep prevention
        keep_alive.sleep_prev.update_activity()
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        params = parse_qs(post_data)

        if self.path == "/add":
            name = params.get('name', [''])[0].strip()
            url = params.get('url', [''])[0].strip()
            email = params.get('email', [''])[0].strip()
            password = params.get('password', [''])[0].strip()
            num_times = int(params.get('num_times', ['1'])[0])
            
            if name and url and num_times > 0:
                added_servers = []
                
                for i in range(1, num_times + 1):
                    server_name = f"{name}-{{{i}}}" if num_times > 1 else name
                    
                    # Check if name already exists
                    if collection.find_one({"name": server_name}):
                        continue
                    
                    server_data = {
                        "name": server_name,
                        "url": url,
                        "email": email if email else "",
                        "password": password if password else "",
                        "created_at": datetime.now(),
                        "status": "pending",
                        "total_pings": 0,
                        "successful_pings": 0,
                        "failed_pings": 0,
                        "consecutive_failures": 0,
                        "last_ping": None,
                        "response_time": 0
                    }
                    
                    collection.insert_one(server_data)
                    added_servers.append(server_name)
                    logger.info(f"➕ Added server: {server_name} - {url}")
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": f"Added {len(added_servers)} server(s)",
                    "servers": added_servers
                }).encode())
            else:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "Missing required fields!"
                }).encode())

        elif self.path == "/remove":
            name = params.get('name', [''])[0].strip()
            if collection.find_one({"name": name}):
                collection.delete_one({"name": name})
                logger.info(f"🗑️ Removed server: {name}")
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "message": "Server removed successfully!"
                }).encode())
            else:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "Server not found!"
                }).encode())
        
        elif self.path == "/remove-by-url":
            url = params.get('url', [''])[0].strip()
            
            if url:
                # Find all servers with this URL
                servers = list(collection.find({"url": url}))
                
                if len(servers) > 0:
                    # Delete all servers
                    server_names = [s['name'] for s in servers]
                    collection.delete_many({"url": url})
                    
                    logger.info(f"🗑️ Removed {len(servers)} server(s) with URL: {url}")
                    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": True,
                        "message": f"Removed {len(servers)} server(s) with URL: {url}",
                        "removed": server_names
                    }).encode())
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "success": False,
                        "message": "No servers found with this URL!"
                    }).encode())
            else:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "message": "URL is required!"
                }).encode())

    def get_main_page(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Ultimate Server Monitor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #667eea;
            --secondary: #764ba2;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #1a202c;
            --light: #f7fafc;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: fadeInDown 0.6s ease;
        }

        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .badge {
            display: inline-block;
            padding: 5px 12px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            margin: 5px;
            font-size: 0.9em;
        }

        .card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            animation: fadeInUp 0.6s ease;
        }

        .card h2 {
            margin-bottom: 20px;
            color: var(--dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            padding: 25px;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-value {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
            font-size: 14px;
        }

        .form-group input {
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            width: 100%;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 8px 15px;
            font-size: 14px;
        }

        .btn-warning {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
            padding: 10px 20px;
            font-size: 14px;
        }

        .server-list {
            display: grid;
            gap: 15px;
        }

        .server-item {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }

        .server-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .server-info {
            flex: 1;
        }

        .server-name {
            font-weight: 700;
            font-size: 18px;
            color: #333;
            margin-bottom: 5px;
        }

        .server-url {
            color: #666;
            font-size: 14px;
            word-break: break-all;
            margin-bottom: 5px;
        }

        .server-credentials {
            font-size: 13px;
            color: #555;
            margin-top: 5px;
        }

        .server-meta {
            display: flex;
            gap: 10px;
            margin-top: 8px;
            flex-wrap: wrap;
        }

        .meta-item {
            font-size: 12px;
            padding: 4px 10px;
            background: white;
            border-radius: 20px;
            color: #666;
        }

        .status-badge {
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            margin-right: 10px;
        }

        .status-online {
            background: var(--success);
            color: white;
        }

        .status-offline {
            background: var(--danger);
            color: white;
        }

        .status-pending {
            background: var(--warning);
            color: white;
        }

        .server-actions {
            display: flex;
            gap: 10px;
            flex-direction: column;
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideInRight 0.4s ease;
        }

        .notification.success { background: var(--success); }
        .notification.error { background: var(--danger); }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes slideInRight {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .header h1 { font-size: 2em; }
            .form-grid { grid-template-columns: 1fr; }
            .server-item { flex-direction: column; align-items: flex-start; }
            .server-actions { flex-direction: row; margin-top: 10px; width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Ultimate Server Monitor</h1>
            <p>Keep your servers alive 24/7 with advanced monitoring</p>
            <div>
                <span class="badge">🔄 Self-Ping Active</span>
                <span class="badge">😴 Sleep Prevention ON</span>
                <span class="badge">🎮 Activity Simulator Running</span>
            </div>
        </div>

        <div class="stats-grid" id="stats">
            <div class="stat-card">
                <div class="stat-value" id="totalServers">0</div>
                <div class="stat-label">Total Servers</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="onlineServers">0</div>
                <div class="stat-label">Online</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="offlineServers">0</div>
                <div class="stat-label">Offline</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalPings">0</div>
                <div class="stat-label">Total Pings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="appUptime">0h</div>
                <div class="stat-label">App Uptime</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="selfPings">0</div>
                <div class="stat-label">Self Pings</div>
            </div>
        </div>

        <div class="card">
            <h2>➕ Add New Server</h2>
            <form id="addForm" onsubmit="addServer(event)">
                <div class="form-grid">
                    <div class="form-group">
                        <label>📝 Server Name</label>
                        <input type="text" name="name" placeholder="My API Server" required>
                    </div>
                    <div class="form-group">
                        <label>🔢 Number of Instances</label>
                        <input type="number" name="num_times" value="1" min="1" max="20" required>
                    </div>
                    <div class="form-group">
                        <label>🌐 Server URL</label>
                        <input type="url" name="url" placeholder="https://api.example.com" required>
                    </div>
                </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label>📧 Email (Optional)</label>
                        <input type="email" name="email" placeholder="admin@example.com">
                    </div>
                    <div class="form-group">
                        <label>🔐 Password (Optional)</label>
                        <input type="password" name="password" placeholder="••••••••">
                    </div>
                </div>
                <button type="submit" class="btn btn-primary">
                    <span id="addBtnText">Add Server</span>
                    <span id="addBtnLoading" class="loading" style="display: none;"></span>
                </button>
            </form>
        </div>

        <div class="card">
            <h2>🗑️ Remove All Servers by URL</h2>
            <form id="removeUrlForm" onsubmit="removeByUrl(event)">
                <div class="form-group">
                    <label>🌐 Enter URL to remove all associated servers</label>
                    <input type="url" name="url" placeholder="https://api.example.com" required>
                </div>
                <button type="submit" class="btn btn-warning" style="width: 100%; margin-top: 10px;">
                    Remove All Servers with This URL
                </button>
            </form>
        </div>

        <div class="card">
            <h2>📋 Active Servers</h2>
            <div class="server-list" id="serverList">
                <div class="empty-state">
                    <p>No servers added yet. Add your first server above!</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }

        async function addServer(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const btn = document.getElementById('addBtnText');
            const loading = document.getElementById('addBtnLoading');
            
            btn.style.display = 'none';
            loading.style.display = 'inline-block';
            
            try {
                const response = await fetch('/add', {
                    method: 'POST',
                    body: new URLSearchParams(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification(result.message, 'success');
                    event.target.reset();
                    loadServers();
                } else {
                    showNotification(result.message, 'error');
                }
            } catch (error) {
                showNotification('Error adding server', 'error');
            } finally {
                btn.style.display = 'inline';
                loading.style.display = 'none';
            }
        }

        async function removeServer(name) {
            if (!confirm(`Are you sure you want to remove "${name}"?`)) return;
            
            try {
                const response = await fetch('/remove', {
                    method: 'POST',
                    body: new URLSearchParams({ name })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification(result.message, 'success');
                    loadServers();
                } else {
                    showNotification(result.message, 'error');
                }
            } catch (error) {
                showNotification('Error removing server', 'error');
            }
        }

        async function removeByUrl(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const url = formData.get('url');
            
            if (!confirm(`Are you sure you want to remove ALL servers with URL: ${url}?`)) return;
            
            try {
                const response = await fetch('/remove-by-url', {
                    method: 'POST',
                    body: new URLSearchParams(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification(result.message + ' - Removed: ' + result.removed.join(', '), 'success');
                    event.target.reset();
                    loadServers();
                } else {
                    showNotification(result.message, 'error');
                }
            } catch (error) {
                showNotification('Error removing servers', 'error');
            }
        }

        async function loadServers() {
            try {
                const response = await fetch('/api/servers');
                const servers = await response.json();
                
                const serverList = document.getElementById('serverList');
                
                if (servers.length === 0) {
                    serverList.innerHTML = `
                        <div class="empty-state">
                            <p>No servers added yet. Add your first server above!</p>
                        </div>
                    `;
                } else {
                    serverList.innerHTML = servers.map(server => {
                        const uptime = calculateUptime(server);
                        return `
                        <div class="server-item">
                            <div class="server-info">
                                <div class="server-name">${server.name}</div>
                                <div class="server-url">🌐 ${server.url}</div>
                                ${server.email || server.password ? `
                                <div class="server-credentials">
                                    ${server.email ? `📧 ${server.email}` : ''} 
                                    ${server.password ? `🔐 ••••••••` : ''}
                                </div>
                                ` : ''}
                                <div class="server-meta">
                                    ${server.response_time ? `<span class="meta-item">⚡ ${server.response_time}ms</span>` : ''}
                                    ${server.last_ping ? `<span class="meta-item">🕒 ${new Date(server.last_ping).toLocaleString()}</span>` : ''}
                                    <span class="meta-item">✅ ${server.successful_pings || 0} / ❌ ${server.failed_pings || 0}</span>
                                    <span class="meta-item">📊 Uptime: ${uptime}%</span>
                                    ${server.consecutive_failures ? `<span class="meta-item" style="background: #fee; color: #c00;">🔴 ${server.consecutive_failures} consecutive failures</span>` : ''}
                                </div>
                            </div>
                            <div class="server-actions">
                                <span class="status-badge status-${server.status || 'pending'}">
                                    ${server.status || 'pending'}
                                </span>
                                <button class="btn btn-danger" onclick="removeServer('${server.name}')">🗑️</button>
                            </div>
                        </div>
                    `}).join('');
                }
                
                // Update stats
                const online = servers.filter(s => s.status === 'online').length;
                const offline = servers.filter(s => s.status === 'offline').length;
                const totalPings = servers.reduce((sum, s) => sum + (s.total_pings || 0), 0);
                
                document.getElementById('totalServers').textContent = servers.length;
                document.getElementById('onlineServers').textContent = online;
                document.getElementById('offlineServers').textContent = offline;
                document.getElementById('totalPings').textContent = totalPings;
                
            } catch (error) {
                console.error('Error loading servers:', error);
            }
        }

        function calculateUptime(server) {
            const total = server.total_pings || 0;
            const successful = server.successful_pings || 0;
            
            if (total === 0) return 0;
            
            return ((successful / total) * 100).toFixed(1);
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('appUptime').textContent = stats.app_uptime_formatted;
                document.getElementById('selfPings').textContent = stats.self_pings;
                
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        // Load data on page load
        loadServers();
        loadStats();
        
        // Auto-refresh
        setInterval(loadServers, 30000);  // Every 30 seconds
        setInterval(loadStats, 10000);     // Every 10 seconds
    </script>
</body>
</html>
        """


def run_server():
    """Run HTTP server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MonitorHandler)
    logger.info("🌐 HTTP Server started on port 8000")
    httpd.serve_forever()


# ==================== MAIN ====================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 ULTIMATE SERVER MONITOR STARTING...")
    logger.info("=" * 60)
    
    # Initialize Keep-Alive System
    keep_alive = UltimateKeepAlive(APP_URL)
    keep_alive.setup()
    
    # Start HTTP server in background
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(2)
    
    logger.info("=" * 60)
    logger.info("✅ ALL SYSTEMS OPERATIONAL")
    logger.info("=" * 60)
    
    try:
        # Run ping loop in main thread
        run_pings()
    except KeyboardInterrupt:
        logger.info("⏹️  Shutting down gracefully...")
        client.close()
        logger.info("👋 Goodbye!")
