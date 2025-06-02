#!/usr/bin/python
# coding=utf-8
# Copyright 2020-2030 - Longsys.

"""
<SCRIPTNAME>bittest.py</SCRIPTNAME>

<DESCRIPTION>
   apl lib
</DESCRIPTION>

<AUTHOR>
    Jeff Zhang
</AUTHOR>

<HISTORY>
    2024/12/12  Jeff Zhang init the script.
</HISTORY>
"""
import serial
import time
import os
import threading

ser = serial.Serial()


class LibApl(object):

    def __init__(self):
        self.baudrate = 115200
        self.bytesize = 8
        self.stopbits = 1
        self.timeout = 5
        self.parity = "N"
        self.timer_thread = None
        self.stop_thread = threading.Event()
        self.cancel_flag = False  # 取消掉电任务的标志位

    def hexshow(self, data):
        hex_data = ''
        hLen = len(data)
        for i in range(hLen):
            hvol = data[i]
            hhex = '%02x' % hvol
            hex_data += hhex + ' '
        print(hex_data)

    def power_on(self, port):
        send_cmd_list = [0xAA, 0x55, 0x00, 0xE5, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x55, 0xAA,
                         0x53, 0x52, 0x6D, 0x0B]
        ser.port = port
        ser.baudrate = self.baudrate
        ser.bytesize = self.bytesize
        ser.stopbits = self.stopbits
        ser.timeout =self.timeout
        ser.parity = self.parity

        ser.open()
        if not ser.isOpen():
            raise serial.SerialException(f"Serial port {port} open fail")

        ser.write(send_cmd_list)
        print("send cmd is: ", end="")
        self.hexshow(send_cmd_list)
        time.sleep(0.5)
        rece_pack_list = ser.readall()
        print("rece cmd is: ", end="")
        self.hexshow(rece_pack_list)

        ser.close()
        if ser.isOpen():
            raise serial.SerialException(f"Serial port {port} close fail")

        print(f"power on cmd send succeed, and serial port {port} close succeed!")


    def power_off(self, port):
        send_cmd_list = [0xAA, 0x55, 0x00, 0xE5, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x55, 0xAA,
                         0xC8, 0xF7, 0x21, 0x64, 0x00]
        ser.port = port
        ser.baudrate = self.baudrate
        ser.bytesize = self.bytesize
        ser.stopbits = self.stopbits
        ser.timeout = self.timeout
        ser.parity = self.parity

        ser.open()
        if not ser.isOpen():
            raise serial.SerialException(f"Serial port {port} open fail")

        ser.write(send_cmd_list)
        print("send cmd is: ", end="")
        self.hexshow(send_cmd_list)
        time.sleep(0.5)
        rece_pack_list = ser.readall()
        print("rece cmd is: ", end="")
        self.hexshow(rece_pack_list)

        ser.close()
        if ser.isOpen():
            raise serial.SerialException(f"Serial port {port} close fail")

        print(f"power off cmd send succeed, and serial port {port} close succeed!")


    def delay_poweroff(self, delay_seconds, port):
        """
        后台线程进行掉电的方法，通过计时器触发。
        delay_seconds：延时时间
        port：串口名称
        """

        if self.timer_thread and self.timer_thread.is_alive():
            print("已有一个掉电线程在运行中")
            return

        self.cancel_flag = False

        self.timer_thread = threading.Thread(target=self._run_delay_poweroff, args=(delay_seconds, port), daemon=True)
        self.timer_thread.start()


    def _run_delay_poweroff(self, delay_seconds, port):
        """
        掉电任务线程，计时并执行掉电。
        """
        print(f"计时开始，{delay_seconds}s后开始掉电\n")
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            if self.cancel_flag:
                print("掉电任务已取消")
                return
            if elapsed_time >= delay_seconds:
                print("执行掉电")
                self.power_off(port=port)
                return
            time.sleep(0.1)



    def cancel_power_off(self):
        """
        取消掉电任务。
        """
        if self.timer_thread and self.timer_thread.is_alive():
            self.cancel_flag = True
            self.timer_thread.join()  # 等待线程结束
            print("掉电任务已成功取消")
        else:
            print("没有正在运行的掉电任务")
