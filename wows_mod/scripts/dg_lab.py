import serial
import threading
import time
import logging
import json
import os
from typing import Dict, Any, Optional

class DGLabController:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.serial = None
        self.connected = False
        self._setup_logging()
        self._connect()

    def _setup_logging(self):
        """设置日志系统"""
        self.logger = logging.getLogger(__name__)

    def _connect(self):
        """连接到DG-Lab控制器"""
        if not self.config['enabled']:
            self.logger.info("DG-Lab控制器功能已禁用")
            return

        try:
            self.serial = serial.Serial(
                port=self.config['port'],
                baudrate=self.config['baud_rate'],
                timeout=1
            )
            self.connected = True
            self.logger.info(f"已连接到DG-Lab控制器: {self.config['port']}")
        except Exception as e:
            self.logger.error(f"连接DG-Lab控制器失败: {e}")
            self.connected = False

    def _calculate_intensity(self, damage: int) -> int:
        """根据伤害值计算强度"""
        mapping = self.config['intensity_mapping']
        min_damage = mapping['min_damage']
        max_damage = mapping['max_damage']
        min_intensity = mapping['min_intensity']
        max_intensity = mapping['max_intensity']

        # 确保伤害值在范围内
        damage = max(min_damage, min(max_damage, damage))
        
        # 计算强度
        intensity = min_intensity + (damage - min_damage) * (max_intensity - min_intensity) / (max_damage - min_damage)
        return int(intensity)

    def send_stimulation(self, damage: int):
        """发送刺激信号"""
        if not self.connected or not self.config['enabled']:
            return

        try:
            intensity = self._calculate_intensity(damage)
            # 构建命令
            command = f"STIM {intensity}\n"
            self.serial.write(command.encode())
            self.logger.debug(f"发送刺激命令: {command.strip()}")
        except Exception as e:
            self.logger.error(f"发送刺激命令失败: {e}")
            self.connected = False

    def stop_stimulation(self):
        """停止刺激"""
        if not self.connected or not self.config['enabled']:
            return

        try:
            command = "STOP\n"
            self.serial.write(command.encode())
            self.logger.debug("发送停止命令")
        except Exception as e:
            self.logger.error(f"发送停止命令失败: {e}")
            self.connected = False

    def close(self):
        """关闭连接"""
        if self.serial and self.serial.is_open:
            self.stop_stimulation()
            self.serial.close()
            self.connected = False
            self.logger.info("已关闭DG-Lab控制器连接")

# 创建DG-Lab控制器实例
g_dg_lab = None

def init_dg_lab(config: Dict[str, Any]):
    """初始化DG-Lab控制器"""
    global g_dg_lab
    g_dg_lab = DGLabController(config)

def close_dg_lab():
    """关闭DG-Lab控制器"""
    global g_dg_lab
    if g_dg_lab:
        g_dg_lab.close()
        g_dg_lab = None 