import sys
import os
import json
from webui import WebUIServer
from dg_lab import DGLabController
import time

def main():
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 初始化DG-Lab控制器
    dg_lab = DGLabController(config['dg_lab'])

    # 启动WebUI服务器
    webui = WebUIServer()
    webui.start()

    try:
        print("模组已启动，按Ctrl+C退出")
        print("WebUI地址: http://localhost:5000")
        
        # 模拟伤害事件
        while True:
            damage = input("输入模拟伤害值(0-10000): ")
            try:
                damage = int(damage)
                if 0 <= damage <= 10000:
                    # 发送到WebUI
                    webui.damage_history.append({
                        "damage": damage,
                        "attacker": {
                            "id": 0,
                            "name": "测试",
                            "type": "测试"
                        },
                        "timestamp": time.time()
                    })
                    # 发送到DG-Lab
                    dg_lab.send_stimulation(damage)
                else:
                    print("伤害值必须在0-10000之间")
            except ValueError:
                print("请输入有效的数字")
    except KeyboardInterrupt:
        print("\n正在关闭...")
    finally:
        webui.stop()
        dg_lab.close()

if __name__ == "__main__":
    main() 