import os
import re
import subprocess
import json
import time
import ctypes
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 将项目根目录添加到 sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import logging
from datetime import datetime
from lib.cmdEnum import BitLockerCommand
from lib.logger_manager import LoggerManager

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging = LoggerManager(log_dir="..\script_log\\",
                        log_name=f"t_Tcg_BitLocker_13_Reboot_{current_time}").get_logger()

class Reboot():

    def __init__(self):
        self.STATE_FILE = r"C:\Users\Administrator\Desktop\bitlockerTest\reboot_sign\bitlocker_state.json"
        self.TASK_NAME = "BitLockerWorkflow"
        self.drive = "D:"
        self.log_dir = "reboot_log"

        # 定义目标脚本和启动目录
        self.base_dir = r"C:\Users\Administrator\Desktop\bitlockerTest"
        self.startup_dir = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
        self.target_script = "test_case\\t_Tcg_BitLocker_13_Reboot.py"  # 修改为目标脚本名
        self.script = "t_Tcg_BitLocker_21_BaseRebootIoTest.py"


    def bitlocker_status_to_dict(self, cmd_response):

        bitlocker_status = {}
        output = cmd_response
        for line in output.splitlines():
            # 匹配格式如 "字段名: 值" 的行
            match = re.match(r'^\s*(.+?):\s+(.+)$', line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                bitlocker_status[key] = value

        return bitlocker_status
    def save_state(self, state):
        with open(self.STATE_FILE, "w") as f:
            json.dump(state, f)


    def load_state(self):
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, "r") as f:
                return json.load(f)
        return {}


    def delete_task(self):
        try:
            subprocess.run(
                f"schtasks /delete /tn {self.TASK_NAME} /f",
                shell=True,
                capture_output=True,
                text=True,
            )
            logging.info("[INFO] Task deleted.")
        except Exception as e:
            logging.exception(f"[ERROR] Failed to delete task: {e}")


    def create_task(self):
        script_path = os.path.abspath(__file__)
        task_command = (
            f'schtasks /create /tn {self.TASK_NAME} /tr "python {script_path}" /sc onstart /f'
        )
        try:
            subprocess.run(task_command, shell=True, check=True)
            logging.info("[INFO] Task created successfully.")
        except Exception as e:
            logging.exception(f"[ERROR] Failed to create task: {e}")


    def enable_bitlocker(self, drive):
        logging.info(f"[INFO] Enabling BitLocker on {drive}...")
        command = f"manage-bde -on {drive} -RecoveryPassword"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"[INFO] BitLocker enabled on {drive}. Output:\n{result.stdout}")
        else:
            logging.warning(f"[ERROR] Failed to enable BitLocker:\n{result.stderr}")
            exit(1)


    def disable_bitlocker(self, drive):
        logging.info(f"[INFO] Disabling BitLocker on {drive}...")
        command = f"manage-bde -off {drive}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"[INFO] BitLocker disabled on {drive}. Output:\n{result.stdout}")
        else:
            logging.warning(f"[ERROR] Failed to disable BitLocker:\n{result.stderr}")

    def create_bat(self):


        # 检查启动目录是否存在
        if not os.path.exists(self.startup_dir):
            raise FileNotFoundError(f"Startup directory not found: {self.startup_dir}")

        # 定义 `.bat` 文件名和路径
        bat_file_name = "run_script.bat"
        bat_file_path = os.path.join(self.startup_dir, bat_file_name)

        # 定义 `bat` 文件内容
        bat_content = f"""@echo off

        %1 %2

        ver|find "5.">nul&&goto :Admin

        mshta vbscript:createobject("shell.application").shellexecute("%~s0","goto :Admin","","runas",1)(window.close)&goto :eof

        :Admin
        @echo off
        REM 激活虚拟环境
        CALL {self.base_dir}\\.venv\\Scripts\\activate.bat

        REM 设置 Python 脚本路径
        SET SCRIPT_PATH={self.base_dir}\\{self.target_script}
        SET LOG_FILE={self.base_dir}\\reboot_log\\{os.path.splitext(self.script)[0]}_log.txt

        REM 运行脚本并保存日志
        python %SCRIPT_PATH% >> %LOG_FILE% 2>&1
        """

        # 创建或替换 `.bat` 文件到启动目录
        with open(bat_file_path, "w", encoding="utf-8") as bat_file:
            bat_file.write(bat_content)

        logging.info(f"Batch file generated and placed in startup directory: {bat_file_path}")

    def Run(self):
        state = self.load_state()  # 加载状态文件
        password = "ZXCVB12345!"
        drive = "D:"
        parent_dir = os.path.dirname(os.getcwd())

        try:
            if state.get("stage") == "enable":
                # 如果状态是启用后的重启
                logging.info("[INFO] Detected post-reboot. Reboot finish...")

                self.delete_task()  # 删除任务
                self.save_state({"stage": "disable"})
                # os.remove(STATE_FILE)  # 删除状态文件
                logging.info("[INFO] Workflow completed successfully.")
            elif state.get("stage") == "disable1":
                # 避免重复启用流程
                logging.info("[INFO] BitLocker is already disabled.")
            else:
                print("state.get: " + str(state.get("stage")))

                logging.info("[INFO] Step 1: start reboot.")
                self.save_state({"stage": "enable"})  # 保存状态
                self.create_task()  # 创建任务
                self.create_bat()
                logging.info("[INFO] System will now reboot...")
                time.sleep(2)
                os.system("shutdown /r /t 1")
        except Exception as e:
            logging.exception(f"发生异常 : {e}")
        finally:
            logging.info("流程完成。")

if __name__ == '__main__':
    if ctypes.windll.shell32.IsUserAnAdmin():
        # 如果已是管理员，则继续执行代码
        logging.info("程序已以管理员权限运行。")
    else:
        # 如果不是管理员，则请求权限并重新启动脚本
        logging.info("尝试以管理员身份运行...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    test = Reboot()
    test.Run()