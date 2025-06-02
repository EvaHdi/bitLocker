#!/usr/bin/python
# coding=utf-8
# Copyright 2020-2030 - Longsys.

"""
<SCRIPTNAME>cmdEnum.py</SCRIPTNAME>

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
import os.path
from enum import Enum
from multiprocessing.spawn import import_main_path
from subprocess import run, CalledProcessError
import subprocess
import time
import pyautogui
import pexpect

# manage-bde -on D: -RecoveryPassword -RecoveryKey C:\Users\ESSD\Desktop\bl
# manage-bde -protectors -add D: -Password
# manage-bde -LOCK d:
# manage-bde -unlock D: -pw

class BitLockerCommand(Enum):
    STATUS = "manage-bde -status {drive}"
    ON = "manage-bde -on {drive} -RecoveryPassword -RecoveryKey {recovery_path}"
    OFF = "manage-bde -off {drive}"
    # LOCK = "manage-bde -lock {drive} -ForceDismount"
    LOCK = "manage-bde -lock {drive}"
    UNLOCK = "manage-bde -unlock {drive} -RecoveryPassword {password}"
    PAUSE = "manage-bde -pause {drive}"
    RESUME = "manage-bde -resume {drive}"
    SET_IDENTIFIER = "manage-bde -SetIdentifier {drive}"
    AUTOUNLOCK_ENABLE = "manage-bde -autounlock -enable {drive}"
    AUTOUNLOCK_DISABLE = "manage-bde -autounlock -disable {drive}"
    PROTECTORS = "manage-bde -protectors -get {drive}"
    CHANGEPASSWORD = "manage-bde -changepassword {drive}"
    CHANGEPIN = "manage-bde -changepin {drive}"
    KEYPACKAGE = "manage-bde -KeyPackage {drive} -Path {key_package_path}"
    UPGRADE = "manage-bde -WipeFreeSpace {drive}"
    FORCERECOVERY = "manage-bde -ForceRecovery {drive}"
    ADD = "manage-bde -protectors -add {drive} -Password"

    # Diskpart command
    DISKPART = "diskpart"
    LISTDISK = "list disk"
    SELECTDISK = "select disk {disknum}"
    SELECTVOLUME = "select volume {volumenum}"
    CREATEPARTITIONPRIMARY = "create partition primary"
    ASSIGNLETTER = "assign letter={disk}"
    FORMAT = "format fs=ntfs quick"
    CONVERTGPT = "convert gpt"
    LISTPARTITION = "list partition"
    EXIT = "exit"

    @staticmethod
    def add_password_protector(drive, new_password):
        """
        添加密码密钥保护器到指定的 BitLocker 卷。

        :param drive: 目标卷（如 "D:"）
        :param new_password: 要添加的密码
        """
        try:
            # 构造 manage-bde 命令
            command = f"manage-bde -protectors -add {drive} -Password"
            # print(f"[DEBUG] Command: {command}")

            # 启动子进程打开交互窗口
            # print("[DEBUG] Starting subprocess...")
            process = subprocess.Popen(command, shell=True)

            # 等待命令窗口启动
            time.sleep(2)  # 等待时间可以根据实际情况调整
            # print("[DEBUG] Subprocess started, simulating password input...")

            # 使用 pyautogui 输入密码并模拟回车
            pyautogui.typewrite(new_password)
            # print(f"[DEBUG] First password entered: {new_password}")
            pyautogui.press("enter")
            # print("[DEBUG] Enter key pressed.")

            time.sleep(1)  # 等待提示再次输入密码
            pyautogui.typewrite(new_password)
            # print(f"[DEBUG] Second password entered: {new_password}")
            pyautogui.press("enter")
            # print("[DEBUG] Enter key pressed.")

            # 等待子进程完成
            process.wait()
            # print("[DEBUG] Subprocess finished.")

            # 检查返回码
            if process.returncode == 0:
                print("[DEBUG] Password protector added successfully.")
            else:
                print("[DEBUG] Failed to add password protector.")
                print(f"[DEBUG] Return code: {process.returncode}")

        except Exception as e:
            print(f"[DEBUG] An unexpected error occurred: {e}")

    @staticmethod
    def change_password(drive, old_password, new_password):
        """
        更改指定 BitLocker 卷的密码。

        :param drive: 目标卷（如 "D:"）
        :param old_password: 当前密码
        :param new_password: 新密码
        """
        try:
            # 构造 manage-bde 命令
            command = f"manage-bde -changepassword {drive}"
            # print(f"[DEBUG] Command: {command}")

            # 启动子进程打开交互窗口
            # print("[DEBUG] Starting subprocess...")
            process = subprocess.Popen(command, shell=True)

            # 等待命令窗口启动
            time.sleep(2)  # 等待时间可以根据实际情况调整
            # print("[DEBUG] Subprocess started, simulating password input...")

            # 输入当前密码并模拟回车
            # pyautogui.typewrite(old_password)
            # print(f"[DEBUG] Old password entered: {old_password}")
            # pyautogui.press("enter")
            # print("[DEBUG] Enter key pressed.")

            time.sleep(1)  # 等待提示输入新密码
            pyautogui.typewrite(new_password)
            # print(f"[DEBUG] New password entered: {new_password}")
            pyautogui.press("enter")
            # print("[DEBUG] Enter key pressed.")

            time.sleep(1)  # 等待提示再次确认新密码
            pyautogui.typewrite(new_password)
            # print(f"[DEBUG] New password re-entered: {new_password}")
            pyautogui.press("enter")
            # print("[DEBUG] Enter key pressed.")

            # 等待子进程完成
            process.wait()
            # print("[DEBUG] Subprocess finished.")

            # 检查返回码
            if process.returncode == 0:
                print("[DEBUG] Password changed successfully.")
            else:
                print("[DEBUG] Failed to change password.")
                print(f"[DEBUG] Return code: {process.returncode}")

        except Exception as e:
            print(f"[DEBUG] An unexpected error occurred: {e}")

    @staticmethod
    def new_volume(drive, disknum, isdisk=False):
        try:
            # 构造 manage-bde 命令
            command = "diskpart"
            print(f"[DEBUG] Command: {command}")

            # 启动子进程打开交互窗口
            print("[DEBUG] Starting subprocess...")
            process = subprocess.Popen(command, shell=True)

            # 等待命令窗口启动
            time.sleep(2)  # 等待时间可以根据实际情况调整
            print("[DEBUG] Subprocess started, simulating password input...")

            # 输入当前密码并模拟回车
            pyautogui.typewrite("list disk")
            pyautogui.press("enter")
            time.sleep(2)
            if isdisk:
                pyautogui.typewrite(f"select disk {disknum}")
                pyautogui.press("enter")
                time.sleep(2)
                pyautogui.typewrite("clean")
                pyautogui.press("enter")
                time.sleep(2)
            pyautogui.typewrite("convert gpt")
            pyautogui.press("enter")
            time.sleep(2)
            pyautogui.typewrite("create partition primary")
            pyautogui.press("enter")
            time.sleep(2)
            pyautogui.typewrite("format fs=ntfs quick")
            pyautogui.press("enter")
            time.sleep(2)
            pyautogui.typewrite(f"assign letter={drive}")
            pyautogui.press("enter")
            time.sleep(2)
            pyautogui.typewrite("list partition")
            pyautogui.press("enter")
            time.sleep(2)
            pyautogui.typewrite("list disk")
            pyautogui.press("enter")
            pyautogui.typewrite("exit")
            pyautogui.press("enter")
        except Exception as e:
            print(f"[DEBUG] An unexpected error occurred: {e}")

    @staticmethod
    def pw_unlock(drive, password):
        try:
            # 构造 manage-bde 命令
            command = f"manage-bde -unlock {drive} -pw"
            # print(f"[DEBUG] Command: {command}")

            # 启动子进程打开交互窗口
            # print("[DEBUG] Starting subprocess...")
            process = subprocess.Popen(command, shell=True)

            # 等待命令窗口启动
            time.sleep(2)  # 等待时间可以根据实际情况调整
            # print("[DEBUG] Subprocess started, simulating password input...")

            # 使用 pyautogui 输入密码并模拟回车
            pyautogui.typewrite(password)
            # print(f"[DEBUG] First password entered: {password}")
            pyautogui.press("enter")
            # print("[DEBUG] Enter key pressed.")

            # 等待子进程完成
            process.wait()
            # print("[DEBUG] Subprocess finished.")

            # 检查返回码
            if process.returncode == 0:
                print("[DEBUG] Password protector added successfully.")
            else:
                print("[DEBUG] Failed to add password protector.")
                print(f"[DEBUG] Return code: {process.returncode}")

        except Exception as e:
            print(f"[DEBUG] An unexpected error occurred: {e}")

    @staticmethod
    def format(drive):
        try:
            # 构造 manage-bde 命令
            command = f"format {drive} /fs:ntfs /q"
            print(f"[DEBUG] Command: {command}")

            # 启动子进程打开交互窗口
            print("[DEBUG] Starting subprocess...")
            process = subprocess.Popen(command, shell=True)

            # 等待命令窗口启动
            time.sleep(2)  # 等待时间可以根据实际情况调整
            print("[DEBUG] Subprocess started, simulating password input...")
            pyautogui.typewrite("Y")
            pyautogui.press("enter")
            time.sleep(2)
            pyautogui.typewrite("Y")
            pyautogui.press("enter")
            time.sleep(2)
            pyautogui.press("enter")

            # 等待子进程完成
            process.wait()
            # print("[DEBUG] Subprocess finished.")

            # 检查返回码
            if process.returncode == 0:
                print("[DEBUG] Password protector added successfully.")
            else:
                print("[DEBUG] Failed to add password protector.")
                print(f"[DEBUG] Return code: {process.returncode}")
        except Exception as e:
            print(f"[DEBUG] An unexpected error occurred: {e}")

    def execute(self, **kwargs):
        """
        Execute the command with the provided arguments.

        Parameters:
            kwargs: Arguments to format into the command (e.g., drive, password, recovery_path).

        Returns:
            str: Command output or error message.
        """
        import subprocess

        # Format command with given arguments
        command = self.value.format(**kwargs)

        # Run command and capture output
        result = subprocess.run(["cmd", "/c", command], capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"错误代码 {result.returncode}: {result.stderr.strip()}"

