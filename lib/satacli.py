#!/usr/bin/python
# coding=utf-8
# Copyright 2020-2030 - Longsys.

"""
<SCRIPTNAME>sedutilCommandEnum.py</SCRIPTNAME>

<DESCRIPTION>
   This is a fundamental calss of tests, which to manage and operate test cases.
</DESCRIPTION>

<AUTHOR>
    HongBo Zhang
</AUTHOR>

<HISTORY>
    2024/11/26  HongBo Zhang init the script.
</HISTORY>
"""
from enum import Enum


class satacliCommandEnum(Enum):
    HELP = "satacli.exe -h > satacli_log\help.txt"
    IDENTIFY = "satacli.exe {disk} id -c {condition} -p > satacli_log\identify.txt"
    # SANITIZE = "satacli.exe 0 sd -F 0x012 -C 0x01 -L 0x426B4572 -p "
    VS_COMMIT = "satacli.exe {disk} cc -o {opcode} -d {dataflow} -F {FEATURE} -L {LBA} -C {COUNT} -p > satacli_log\commit.txt"

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
        print(f"command : {command}")

        # Run command and capture output
        result = subprocess.run(["cmd", "/c", command], capture_output=True, text=True, shell=True)

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"错误代码 {result.returncode}: {result.stderr.strip()}"