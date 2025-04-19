from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import threading
import logging
import time
from typing import Dict, List, Any

# 全局变量
app = Flask(__name__)
CORS(app)
server_thread = None
damage_history: List[Dict[str, Any]] = []
last_damage_time = 0

@app.route('/')
def index():
    """渲染主页面"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """返回服务器状态"""
    return jsonify({
        'status': 'running',
        'last_damage_time': last_damage_time,
        'damage_count': len(damage_history)
    })

@app.route('/api/damage', methods=['POST'])
def receive_damage():
    """接收伤害数据"""
    global last_damage_time
    try:
        data = request.get_json()
        if not data or 'damage' not in data:
            return jsonify({'error': 'Invalid data format'}), 400
            
        # 更新最后伤害时间
        last_damage_time = time.time()
        
        # 添加时间戳
        data['server_time'] = last_damage_time
        
        # 添加到历史记录
        damage_history.append(data)
        
        # 保持历史记录在100条以内
        if len(damage_history) > 100:
            damage_history.pop(0)
            
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"处理伤害数据时出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """获取伤害历史记录"""
    return jsonify(damage_history)

def start_webui():
    """启动WebUI服务器"""
    global server_thread
    if server_thread is None or not server_thread.is_alive():
        server_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5001))
        server_thread.daemon = True
        server_thread.start()
        logging.info("WebUI服务器已启动")

def stop_webui():
    """停止WebUI服务器"""
    # Flask服务器会在主线程退出时自动停止
    logging.info("WebUI服务器已停止") 