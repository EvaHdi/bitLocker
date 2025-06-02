import logging
import os
from datetime import datetime

class LoggerManager:
    def __init__(self, log_dir="logs", log_name=None, level=logging.DEBUG):
        """
        初始化日志管理器
        :param log_dir: 日志文件夹路径，默认为 "logs"
        :param log_name: 日志文件名称（不含扩展名），默认为当前时间
        :param level: 日志级别，默认为 DEBUG
        """
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        if not log_name:
            log_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = os.path.join(self.log_dir, f"{log_name}.log")

        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(log_file, mode="w", encoding="utf-8"),
                logging.StreamHandler()  # 控制台输出
            ]
        )

        self.logger = logging.getLogger()

    def get_logger(self):
        """
        获取日志记录器实例
        :return: 日志记录器
        """
        return self.logger