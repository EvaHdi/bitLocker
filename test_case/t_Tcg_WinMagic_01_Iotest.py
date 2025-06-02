import re
import os
import ctypes, sys
import io

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 将项目根目录添加到 sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from lib.sedutilCommandEnum import sedutilCommandEnum
import traceback
from datetime import datetime
import time
from lib.smartcli import smartcliCommandEnum
from lib.logger_manager import LoggerManager
from lib.cmdEnum import BitLockerCommand
import subprocess
import shutil


current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging = LoggerManager(log_dir="..\script_log\\",
                        log_name=f"t_Tcg_WinMagic_01_Iotest_{current_time}").get_logger()

# 配置路径和参数
drive_letter = "D:"
test_dir = os.path.join(drive_letter, "fio_test")
fio_executable = "fio.exe"  # 确保 `fio` 在系统 PATH 中
fio_log_dir = os.path.join(test_dir, "fio_log")
# fio_file_template = os.path.join(test_dir, "testfile")
fio_file_template = "testfile"
test_dir1 = "D\:\\fio_test"

# 确保测试目录和日志目录存在
os.makedirs(test_dir, exist_ok=True)
os.makedirs(fio_log_dir, exist_ok=True)
class Iotest():
    def __init__(self):
        logging.info("FIO read write")
        test_dir = "D:\\fio_test"
        test_file = "testfile"
        fio_path = "fio.exe"
        fio_test_dir = "D\:\\fio_test"

    def get_available_space(self, drive):
        """获取磁盘剩余空间 (字节)。"""
        total, used, free = shutil.disk_usage(drive)
        return free

    # 填盘至99%的顺序写
    def fill_disk_to_99(self):
        logging.info("Step 1: Filling disk to 99% with sequential write...")
        available_space = self.get_available_space(drive_letter)
        target_size = int(available_space * 0.50)  # 填充到99%空间
        fill_command = (
            f"{fio_executable} --name=seqwrite --rw=write --bs=128k --size={target_size} "
            f"--directory={test_dir1} --filename={fio_file_template} --iodepth=1 "
            f"--verify=crc32 --output={os.path.join('fio_log', 'filldisk.log')}"
        )
        try:
            subprocess.run(fill_command, check=True, shell=True)
            logging.info("Disk fill completed successfully.")
        except subprocess.CalledProcessError as e:
            logging.exception(f"Error during disk fill: {e}")
            raise

    # 混合读写测试
    def mixed_rw_test(self):
        logging.info("Step 2: Running mixed sequential and random read/write test...")
        available_space = self.get_available_space(drive_letter)
        target_size = int(available_space * 0.99)
        mixed_command = (
            f"{fio_executable} --name=mixed_rw --rw=randrw --rwmixread=50 --bs=128k "
            f"--size={target_size} --directory={test_dir1} --filename={fio_file_template} "
            f"--iodepth=4 --verify=crc32 --output={os.path.join('fio_log', 'mixrw.log')}"
        )
        try:
            subprocess.run(mixed_command, check=True, shell=True)
            logging.info("Mixed read/write test completed successfully.")
        except subprocess.CalledProcessError as e:
            logging.exception(f"Error during mixed read/write test: {e}")
            raise

    # 数据校验
    def verify_data(self):
        logging.info("Step 3: Verifying written data...")
        verify_command = (
            f"{fio_executable} --name=verify_data --verify_only=1 "
            f"--directory={test_dir1} --filename={fio_file_template} "
            f"--output={os.path.join('fio_log', 'verify.log')}"
        )
        try:
            subprocess.run(verify_command, check=True, shell=True)
            logging.info("Data verification completed successfully.")
        except subprocess.CalledProcessError as e:
            logging.exception(f"Error during data verification: {e}")
            raise

    # 清理测试数据
    def cleanup_test_data(self):
        logging.info("Step 4: Cleaning up test data...")
        try:
            for root, dirs, files in os.walk(test_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(test_dir)
            logging.info("Test data cleaned up successfully.")
        except Exception as e:
            logging.exception(f"Error during cleanup: {e}")
            raise

    def Run(self):
        try:
            self.fill_disk_to_99()
            self.mixed_rw_test()
            self.verify_data()
        finally:
            self.cleanup_test_data()

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        # 如果已是管理员，则继续执行代码
        logging.info("程序已以管理员权限运行。")
    else:
        # 如果不是管理员，则请求权限并重新启动脚本
        logging.info("尝试以管理员身份运行...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    test = Iotest()
    test.Run()

