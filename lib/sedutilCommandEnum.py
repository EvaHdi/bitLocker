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


class sedutilCommandEnum(Enum):
    SCAN = "sedutil-cli.exe --scan"
    QUERY = "sedutil-cli.exe --query \\\\.\PhysicalDrive{DiskNum}"
    PRINTDEFAULTPASSWORD = "sedutil-cli.exe --printDefaultPassword \\\\.\PhysicalDrive{DiskNum}"
    INITIALSETUP = "sedutil-cli.exe --initialsetup {MSID} \\\\.\PhysicalDrive{DiskNum}"
    DISABLELOCKINGRANGE = ("sedutil-cli.exe "
                           "--disableLockingRange {rangeId} {MSID} \\\\.\PhysicalDrive{DiskNum}")
    LISTLOCKINGRANGES = "sedutil-cli.exe --listLockingRanges {MSID} \\\\.\PhysicalDrive{DiskNum}"
    SETLOCKINGRANGE = ("sedutil-cli.exe "
                       "--setupLockingRange {rangeId} {start} {size} {MSID} \\\\.\PhysicalDrive{DiskNum}")
    PSIDREVERT = ("sedutil-cli.exe "
                  "--yesIreallywanttoERASEALLmydatausingthePSID {PSID} \\\\.\PhysicalDrive{DiskNum}")
    GETDISKSEIZE = "wmic diskdrive get size"

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