# WGGameDGLABPlayer 模组

这是一个用于《战舰世界》的模组，用于实时监控游戏中的伤害数据并通过WebUI与DG-Lab设备进行交互。

## 功能特点

- 实时监控游戏中的伤害数据
- 通过WebUI与DG-Lab设备进行交互
- 可配置的连接检查间隔
- 详细的日志记录
- 调试模式支持

## 安装说明

1. 将模组文件夹 `WGGameDGLABPlayer` 复制到游戏安装目录的 `res/scripts/client/gui/mods/` 文件夹中
2. 确保已安装 `python-requests` 库（版本 2.31.0 或更高）
3. 启动游戏并启用模组

## 配置说明

模组配置文件 `config.json` 包含以下选项：

- `webui_url`: WebUI的URL地址（默认为 http://localhost:5000）
- `connection_check_interval`: 连接检查间隔（秒）
- `debug_mode`: 是否启用调试模式
- `log_level`: 日志级别（INFO/DEBUG/ERROR）

## 注意事项

- 请确保WebUI服务正在运行
- 建议在游戏开始前检查模组连接状态
- 如遇到问题，请查看游戏日志文件 