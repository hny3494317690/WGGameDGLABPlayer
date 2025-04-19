from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import threading
import time
import json
import logging
import os
from typing import Dict, List, Any

class WebUIServer:
    def __init__(self):
        self.app = Flask(__name__, 
                        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                        static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        CORS(self.app)
        self.damage_history: List[Dict[str, Any]] = []
        self.server_thread = None
        self.running = False
        self._setup_routes()
        self._setup_logging()

    def _setup_logging(self):
        """设置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _setup_routes(self):
        """设置API路由"""
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/status', methods=['GET'])
        def status():
            return jsonify({
                'status': 'running',
                'damage_history_count': len(self.damage_history)
            })

        @self.app.route('/api/damage', methods=['POST'])
        def receive_damage():
            try:
                data = request.json
                if not data or 'damage' not in data:
                    return jsonify({'error': 'Invalid data format'}), 400
                
                self.damage_history.append(data)
                self.logger.info(f"收到伤害数据: {data}")
                return jsonify({'status': 'success'})
            except Exception as e:
                self.logger.error(f"处理伤害数据时出错: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/damage/history', methods=['GET'])
        def get_damage_history():
            return jsonify(self.damage_history)

        @self.app.route('/api/damage/clear', methods=['POST'])
        def clear_damage_history():
            self.damage_history = []
            return jsonify({'status': 'success'})

    def start(self, host='0.0.0.0', port=5000):
        """启动WebUI服务器"""
        if self.running:
            return
        
        def run_server():
            self.running = True
            self.app.run(host=host, port=port, debug=False)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.logger.info(f"WebUI服务器已启动，监听地址: {host}:{port}")

    def stop(self):
        """停止WebUI服务器"""
        if not self.running:
            return
        
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=1)
        self.logger.info("WebUI服务器已停止")

# 创建WebUI服务器实例
g_webui_server = WebUIServer()

def start_webui():
    """启动WebUI服务器"""
    g_webui_server.start()

def stop_webui():
    """停止WebUI服务器"""
    g_webui_server.stop()