import BigWorld
import BattleReplay
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE
import json
import requests
import threading
import time
import logging
import os
from typing import Dict, Any, Optional
from .webui import start_webui, stop_webui
from .dg_lab import init_dg_lab, close_dg_lab

class WGGameDGLABPlayerWoT(object):
    def __init__(self):
        self.connected = False
        self.last_damage = 0
        self.config = self._load_config()
        self._setup_logging()
        self.check_connection()
        init_dg_lab(self.config['dg_lab'])  # 初始化DG-Lab控制器
        logger.info("WGGameDGLABPlayerWoT模组初始化完成")

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 验证配置
                required_fields = ['webui_url', 'connection_check_interval', 'debug_mode', 'log_level', 'dg_lab']
                for field in required_fields:
                    if field not in config:
                        raise ValueError(f"配置文件中缺少必需的字段: {field}")
                return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {
                "webui_url": "http://localhost:5001",
                "connection_check_interval": 5,
                "debug_mode": False,
                "log_level": "INFO",
                "dg_lab": {
                    "enabled": False,
                    "port": "COM3",
                    "baud_rate": 9600,
                    "intensity_mapping": {
                        "min_damage": 0,
                        "max_damage": 1000,
                        "min_intensity": 0,
                        "max_intensity": 100
                    }
                }
            }

    def _setup_logging(self):
        """设置日志系统"""
        log_level = getattr(logging, self.config['log_level'].upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        global logger
        logger = logging.getLogger(__name__)

    def check_connection(self):
        """检查与WebUI的连接状态"""
        def connection_checker():
            while True:
                try:
                    response = requests.get(f"{self.config['webui_url']}/api/status", timeout=2)
                    if response.status_code == 200:
                        if not self.connected:
                            logger.info("已连接到WebUI服务器")
                            self.connected = True
                    else:
                        if self.connected:
                            logger.warning("WebUI服务器连接断开")
                            self.connected = False
                except Exception as e:
                    if self.connected:
                        logger.error(f"连接WebUI服务器失败: {e}")
                        self.connected = False
                time.sleep(self.config['connection_check_interval'])

        thread = threading.Thread(target=connection_checker)
        thread.daemon = True
        thread.start()

    def onPlayerDamaged(self, attackerID: int, damage: int):
        """处理玩家受到伤害的事件"""
        if not self.connected:
            return
            
        try:
            # 获取攻击者信息
            attacker = BigWorld.entity(attackerID)
            if attacker is None:
                return
                
            # 准备发送的数据
            data = {
                "damage": damage,
                "attacker": {
                    "id": attackerID,
                    "name": attacker.name if hasattr(attacker, 'name') else "Unknown",
                    "type": attacker.typeDescriptor.type if hasattr(attacker, 'typeDescriptor') else "Unknown"
                },
                "timestamp": time.time()
            }
            
            # 发送数据到WebUI
            if self.connected:
                response = requests.post(
                    f"{self.config['webui_url']}/api/damage",
                    json=data,
                    timeout=2
                )
                if response.status_code != 200:
                    logger.error(f"发送伤害数据失败: {response.status_code}")
                elif self.config['debug_mode']:
                    logger.debug(f"成功发送伤害数据: {data}")

            # 发送刺激信号到DG-Lab控制器
            from .dg_lab import g_dg_lab
            if g_dg_lab and g_dg_lab.connected:
                g_dg_lab.send_stimulation(damage)
                
        except Exception as e:
            logger.error(f"处理伤害数据时出错: {e}")

# 创建模组实例
g_WGGameDGLABPlayerWoT = WGGameDGLABPlayerWoT()

# 注册事件处理
def onPlayerDamaged(attackerID: int, damage: int):
    g_WGGameDGLABPlayerWoT.onPlayerDamaged(attackerID, damage)

# 注册到游戏事件系统
def init():
    try:
        from gui.battle_control import g_battleControl
        g_battleControl.onPlayerDamaged += onPlayerDamaged
        start_webui()  # 启动WebUI服务器
        logger.info("WGGameDGLABPlayerWoT模组已初始化")
    except Exception as e:
        logger.error(f"模组初始化失败: {e}")

def fini():
    try:
        from gui.battle_control import g_battleControl
        g_battleControl.onPlayerDamaged -= onPlayerDamaged
        stop_webui()  # 停止WebUI服务器
        close_dg_lab()  # 关闭DG-Lab控制器
        logger.info("WGGameDGLABPlayerWoT模组已关闭")
    except Exception as e:
        logger.error(f"模组关闭时出错: {e}") 