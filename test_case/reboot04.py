import os
import shutil

# 定义目标脚本和启动目录
base_dir = r"C:\Users\Administrator\Desktop\code\bitlockerTest"
startup_dir = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"
target_script = "t_Tcg_BitLocker_14_RebootAPL.py"  # 修改为目标脚本名

# 检查启动目录是否存在
if not os.path.exists(startup_dir):
    raise FileNotFoundError(f"Startup directory not found: {startup_dir}")

# 定义 `.bat` 文件名和路径
bat_file_name = "run_script.bat"
bat_file_path = os.path.join(startup_dir, bat_file_name)

# 定义 `bat` 文件内容
bat_content = f"""@echo off

%1 %2

ver|find "5.">nul&&goto :Admin

mshta vbscript:createobject("shell.application").shellexecute("%~s0","goto :Admin","","runas",1)(window.close)&goto :eof

:Admin
@echo off
REM 激活虚拟环境
CALL {base_dir}\\.venv\\Scripts\\activate.bat

REM 设置 Python 脚本路径
SET SCRIPT_PATH={base_dir}\\{target_script}
SET LOG_FILE={base_dir}\\reboot_log\\{os.path.splitext(target_script)[0]}_log.txt

REM 运行脚本并保存日志
python %SCRIPT_PATH% >> %LOG_FILE% 2>&1
"""

# 创建或替换 `.bat` 文件到启动目录
with open(bat_file_path, "w", encoding="utf-8") as bat_file:
    bat_file.write(bat_content)

print(f"Batch file generated and placed in startup directory: {bat_file_path}")
