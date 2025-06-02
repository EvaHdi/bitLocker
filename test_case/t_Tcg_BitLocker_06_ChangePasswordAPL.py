#!/usr/bin/python
# coding=utf-8
# Copyright 2020-2030 - Longsys.

"""
<SCRIPTNAME>bittest.py</SCRIPTNAME>

<DESCRIPTION>
   This is a fundamental calss of tests, which to manage and operate test cases.
</DESCRIPTION>

<AUTHOR>
    HongBo Zhang
</AUTHOR>

<HISTORY>
    2024/11/12  HongBo Zhang init the script.
</HISTORY>
"""
import re
import os
import ctypes, sys
import io

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 将项目根目录添加到 sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import time
import traceback
from datetime import datetime
from lib.smartcli import smartcliCommandEnum
from lib.logger_manager import LoggerManager
from lib.cmdEnum import BitLockerCommand
from lib.lib_apl import LibApl


current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logging = LoggerManager(log_dir="..\script_log\\",
                        log_name=f"t_Tcg_BitLocker_06_ChangePasswordAPL_{current_time}").get_logger()

class ChangePasswordAPL():

    def __init__(self):
        self.drive = "D:"
        self.key_file = "key.txt"
        self.transition_state = "转换状态"
        self.locked_state = "锁定状态"

        self.complete_decryption = "完全解密"
        self.encrypting = "加密中"
        self.complete_encryption = "完全加密"
        self.locked = "已锁定"
        self.unlocked = "已解锁"

        self.key = "1MD9VRYEUUPPR4QM76AFCEZAQ70M8T4S"
        self.password = "ZXCVB12345!"
        self.new_password = "ZXCVB12345"
        self.apl_lib = LibApl()


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

    def verify_locked(self, drive_letter="D://"):
        """
        验证指定盘符是否被锁定。
        :param drive_letter: 目标盘符，例如 'D:'
        :return: True 表示锁定，False 表示未锁定
        """
        test_file = os.path.join(drive_letter, "test_file.txt")

        # 测试写入操作
        try:
            with open(test_file, "w") as file:
                file.write("This is a test.")
            # 如果写入成功，说明未锁定
            logging.info("写入成功，卷未锁定。")
            os.remove(test_file)  # 清理测试文件
            return False
        except PermissionError:
            logging.exception("写入失败，卷可能被锁定。")
        except OSError as e:
            logging.exception(f"写入失败，错误信息：{e}")

        # 测试读取操作
        try:
            files = os.listdir(drive_letter)
            logging.info("读取成功，卷未锁定。")
            return False
        except PermissionError:
            logging.exception("读取失败，卷可能被锁定。")
        except OSError as e:
            logging.exception(f"读取失败，错误信息：{e}")

        return True

    def Run(self):
        try:
            # logging.info("step 0 new volume")
            # BitLockerCommand.new_volume(drive="D", disknum="0", isdisk=True)
            # parent_dir = os.path.dirname(os.getcwd())
            #
            # logging.info("step 1: bitlocker on")
            # output = BitLockerCommand.STATUS.execute(drive=self.drive)
            # logging.info(output)
            # disk_current_status = self.bitlocker_status_to_dict(output)
            # parent_dir = os.path.dirname(os.getcwd())
            # revoverykeydir = os.path.join(parent_dir, "revoverykey")
            # if disk_current_status[self.transition_state] == self.complete_decryption:
            #     output = BitLockerCommand.ON.execute(drive=self.drive, recovery_path=parent_dir)
            #     file_path = os.path.join(revoverykeydir, self.key_file)
            #     with open(file_path, "w", encoding="utf-8") as file:
            #         file.write(output)
            #
            #     # 使用正则表达式提取recoverkey
            #     password_match = re.search(r"密码:\s+(\d{6}(?:-\d{6}){7})", output)
            #     password = password_match.group(1) if password_match else None
            #     logging.info(f"key: {password}")
            logging.info("step 1: bitlocker unlock")
            BitLockerCommand.pw_unlock(drive=self.drive, password=self.password)
            time.sleep(1)
            current_locked_state = (
                self.bitlocker_status_to_dict(BitLockerCommand.STATUS.execute(drive=self.drive)))[self.locked_state]

            logging.info(f"current_locked_state : {current_locked_state}")
            assert current_locked_state == self.unlocked, "current_locked_state is error!"
            logging.info("step 2: bitlocker change password")
            BitLockerCommand.change_password(drive=self.drive, old_password=self.password,
                                             new_password=self.new_password)

            logging.info("step 3: delay power off")
            port = 'COM4'  # 串口名称
            delay_seconds = 10
            self.apl_lib.delay_poweroff(delay_seconds=delay_seconds, port=port)

            start_time = time.time()
            while time.time() - start_time < 30:
                logging.info("识盘命令输出：")
                smart_log = smartcliCommandEnum.ALL.execute(disk="/dev/sda")
                logging.info(f"smart_log : {smart_log}")
                time.sleep(1)

            logging.info("等待5秒后开始上电")
            time.sleep(5)
            self.apl_lib.power_on(port=port)

            time.sleep(60)
            current_transition_state = (
                self.bitlocker_status_to_dict(BitLockerCommand.STATUS.execute(drive=self.drive)))[self.locked_state]
            logging.info(f"current_transition_state : {current_transition_state}")
            assert current_transition_state == self.locked, "current_transition_state is error!"
        except Exception as e:
            logging.exception("发生异常：", e)  # 打印异常简要信息
            logging.exception("详细错误信息：")
            traceback.print_exc()
            input("Press Enter to exit...")
        finally:
            pass


if __name__ == '__main__':
    if ctypes.windll.shell32.IsUserAnAdmin():
        # 如果已是管理员，则继续执行代码
        logging.info("程序已以管理员权限运行。")
    else:
        # 如果不是管理员，则请求权限并重新启动脚本
        logging.info("尝试以管理员身份运行...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    test = ChangePasswordAPL()
    test.Run()
