logging.info("step 0: delay power off")
port = 'COM4'  # 串口名称
delay_seconds = 3.5
self.lib.delay_poweroff(delay_seconds=delay_seconds, port=port)

logging.info("step 1: bitlocker unlock")
BitLockerCommand.pw_unlock(drive=self.drive, password=self.new_password)
time.sleep(1)
current_locked_state = (
    self.bitlocker_status_to_dict(BitLockerCommand.STATUS.execute(drive=self.drive)))[self.locked_state]

logging.info(f"current_locked_state : {current_locked_state}")
assert current_locked_state == self.unlocked, "current_locked_state is error!"

start_time = time.time()
while time.time() - start_time < 10:
    logging.info("识盘命令输出：")
    smart_log = smartcliCommandEnum.ALL.execute(disk="/dev/sda")
    logging.info(f"smart_log : {smart_log}")
    time.sleep(1)

logging.info("等待15秒后开始上电")
time.sleep(15)
self.lib.power_on(port=port)