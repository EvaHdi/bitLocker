import os
import subprocess
import json
import time
import ctypes
import sys
import logging
from datetime import datetime
import base01
from lib.cmdEnum import BitLockerCommand
from lib.logger_manager import LoggerManager


STATE_FILE = r"C:\Users\ESSD\Desktop\code\bitlockerTest\reboot_sign\bitlocker_state.json"
TASK_NAME = "BitLockerWorkflow"
drive = "D:"
log_dir = "reboot_log"
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logger = LoggerManager(log_dir="reboot_log", log_name=f"log_{current_time}").get_logger()
# manage-bde -on D: -PW
# manage-bde -status D:
# manage-bde -off D:
# manage-bde -lock D:
# sedutil-cli.exe --yesIreallywanttoERASEALLmydatausingthePSID {PSID} \\.\PhysicalDrive*

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def delete_task():
    try:
        subprocess.run(
            f"schtasks /delete /tn {TASK_NAME} /f",
            shell=True,
            capture_output=True,
            text=True,
        )
        logging.info("[INFO] Task deleted.")
    except Exception as e:
        logging.exception(f"[ERROR] Failed to delete task: {e}")


def create_task():
    script_path = os.path.abspath(__file__)
    task_command = (
        f'schtasks /create /tn {TASK_NAME} /tr "python {script_path}" /sc onstart /f'
    )
    try:
        subprocess.run(task_command, shell=True, check=True)
        logging.info("[INFO] Task created successfully.")
    except Exception as e:
        logging.exception(f"[ERROR] Failed to create task: {e}")


def enable_bitlocker(drive):
    logging.info(f"[INFO] Enabling BitLocker on {drive}...")
    command = f"manage-bde -on {drive} -RecoveryPassword"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        logging.info(f"[INFO] BitLocker enabled on {drive}. Output:\n{result.stdout}")
    else:
        logging.warning(f"[ERROR] Failed to enable BitLocker:\n{result.stderr}")
        exit(1)


def disable_bitlocker(drive):
    logging.info(f"[INFO] Disabling BitLocker on {drive}...")
    command = f"manage-bde -off {drive}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        logging.info(f"[INFO] BitLocker disabled on {drive}. Output:\n{result.stdout}")
    else:
        logging.warning(f"[ERROR] Failed to disable BitLocker:\n{result.stderr}")


def main():
    if ctypes.windll.shell32.IsUserAnAdmin():
        # 如果已是管理员，则继续执行代码
        logging.info("程序已以管理员权限运行。")
    else:
        # 如果不是管理员，则请求权限并重新启动脚本
        logging.warning("尝试以管理员身份运行...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    state = load_state()  # 加载状态文件
    password = "ZXCVB12345!"
    drive = "D:"
    parent_dir = os.path.dirname(os.getcwd())

    try:
        if state.get("stage") == "enable":
            # 如果状态是启用后的重启
            logging.info("[INFO] Detected post-reboot. Running disable BitLocker logic...")
            BitLockerCommand.pw_unlock(drive=drive, password=password)
            time.sleep(1)
            BitLockerCommand.OFF.execute(drive=drive)
            delete_task()  # 删除任务
            save_state({"stage": "disable"})
            # os.remove(STATE_FILE)  # 删除状态文件
            logging.info("[INFO] Workflow completed successfully.")
        elif state.get("stage") == "disable1":
            # 避免重复启用流程
            logging.info("[INFO] BitLocker is already disabled.")
        else:
            print("state.get: " + str(state.get("stage")))
            # 初次运行：启用 BitLocker 并设置状态文件
            logging.info("[INFO] Initial run. Running enable BitLocker logic...")
            output = BitLockerCommand.ON.execute(drive=drive, recovery_path=parent_dir)
            logging.info("step 1: status check")
            output = BitLockerCommand.STATUS.execute(drive=drive)
            logging.info(output)
            BitLockerCommandMethod = base01.BitLockerTest01()
            disk_current_status = BitLockerCommandMethod.bitlocker_status_to_dict(output)["加密方法"]
            logging.info(f"disk_current_status : {disk_current_status}")
            assert "硬件加密" in disk_current_status, "disk status is error!"
            time.sleep(3)
            logging.info("step : bitlocker add password")
            BitLockerCommand.add_password_protector(drive=drive, new_password=password)
            time.sleep(5)

            save_state({"stage": "enable"})  # 保存状态
            create_task()  # 创建任务

            logging.info("[INFO] System will now reboot...")
            time.sleep(2)
            os.system("shutdown /r /t 1")
    except Exception as e:
        logging.exception("发生异常：", e)
    finally:
        logging.info("流程完成。")

if __name__ == '__main__':
    main()