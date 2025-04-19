import serial
import serial.tools.list_ports
import logging
import time
from typing import Dict, Any, Optional

class DGLabController:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connected = False
        self.serial_port: Optional[serial.Serial] = None
        self._connect()

    def _connect(self):
        """连接到DG-Lab设备"""
        if not self.config.get('enabled', False):
            logging.info("DG-Lab控制器已禁用")
            return

        try:
            # 查找可用的串口
            ports = serial.tools.list_ports.comports()
            target_port = None
            
            # 如果配置了特定端口，尝试使用它
            if 'port' in self.config:
                for port in ports:
                    if port.device == self.config['port']:
                        target_port = port.device
                        break
            
            # 如果没有找到配置的端口，使用第一个可用端口
            if not target_port and ports:
                target_port = ports[0].device
                logging.warning(f"未找到配置的端口 {self.config.get('port')}，使用 {target_port}")

            if not target_port:
                raise Exception("未找到可用的串口")

            # 打开串口
            self.serial_port = serial.Serial(
                port=target_port,
                baudrate=self.config.get('baud_rate', 9600),
                timeout=1
            )
            
            # 测试连接
            self._test_connection()
            self.connected = True
            logging.info(f"已连接到DG-Lab设备: {target_port}")
            
        except Exception as e:
            logging.error(f"连接DG-Lab设备失败: {e}")
            self.connected = False

    def _test_connection(self):
        """测试与DG-Lab设备的连接"""
        if not self.serial_port:
            raise Exception("串口未初始化")
            
        # 发送测试命令
        self.serial_port.write(b'AT\r\n')
        time.sleep(0.1)
        response = self.serial_port.readline()
        
        if not response or b'OK' not in response:
            raise Exception("设备响应异常")

    def send_stimulation(self, damage: int):
        """根据伤害值发送刺激信号"""
        if not self.connected or not self.serial_port:
            return
            
        try:
            # 获取强度映射配置
            mapping = self.config.get('intensity_mapping', {})
            min_damage = mapping.get('min_damage', 0)
            max_damage = mapping.get('max_damage', 1000)
            min_intensity = mapping.get('min_intensity', 0)
            max_intensity = mapping.get('max_intensity', 100)
            
            # 计算刺激强度
            damage = max(min_damage, min(damage, max_damage))
            intensity = int(min_intensity + (damage - min_damage) * (max_intensity - min_intensity) / (max_damage - min_damage))
            
            # 发送刺激命令
            command = f"STIM {intensity}\r\n"
            self.serial_port.write(command.encode())
            
            if self.config.get('debug_mode', False):
                logging.debug(f"发送刺激信号: 伤害={damage}, 强度={intensity}")
                
        except Exception as e:
            logging.error(f"发送刺激信号失败: {e}")
            self.connected = False

    def close(self):
        """关闭连接"""
        if self.serial_port:
            try:
                self.serial_port.close()
            except Exception as e:
                logging.error(f"关闭串口失败: {e}")
        self.connected = False
        logging.info("DG-Lab控制器已关闭")

# 全局实例
g_dg_lab: Optional[DGLabController] = None

def init_dg_lab(config: Dict[str, Any]):
    """初始化DG-Lab控制器"""
    global g_dg_lab
    if g_dg_lab is None:
        g_dg_lab = DGLabController(config)

def close_dg_lab():
    """关闭DG-Lab控制器"""
    global g_dg_lab
    if g_dg_lab:
        g_dg_lab.close()
        g_dg_lab = None 