# -*- coding: utf-8 -*-

import sys
import struct
import urllib.parse
import re
import subprocess
import datetime
import json
import os
import logging
import logging.handlers
import ctypes
import ctypes.wintypes

def get_response():
    msg_len = sys.stdin.buffer.read(4)
    if not msg_len:
        logger.info('msg_len error')
        logger.info("end:%s" % datetime.datetime.now())
        return None
    msg_len = struct.unpack('=I', msg_len)[0]
    msg = sys.stdin.buffer.read(msg_len).decode("utf-8")
    logging.info('recieved msg(len=%s):%s' % (msg_len, msg))
    return msg

def send_response(msg):
    encoded_msg = json.dumps(msg).encode("utf-8")
    sys.stdout.buffer.write(struct.pack('=I', len(encoded_msg)))
    sys.stdout.buffer.write(struct.pack(str(len(encoded_msg))+"s",encoded_msg))
    sys.stdout.buffer.flush()

# ログ設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)8s %(message)s")
# 　コンソール出力
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
# 　ファイル出力
handler = logging.handlers.RotatingFileHandler(filename = 'result.log', maxBytes = 1000000, backupCount = 3)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("start:%s" % datetime.datetime.now())

# 実行ファイル取得
pid = ctypes.c_ulong()
ctypes.windll.user32.GetWindowThreadProcessId(ctypes.windll.user32.GetForegroundWindow(), ctypes.pointer(pid))
cmd = 'wmic process where "processid = ' + str(pid.value) + '" get ExecutablePath'
res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
if res and res.stdout:
    res = res.stdout.decode('cp932').split('\r\n')
    if len(res) >= 2:
        exe_path = res[1]
else:
    logger.info('ExecutablePath not found: pid=%d', pid.value)
    logger.info("end:%s" % datetime.datetime.now())
    sys.exit(0)

# キーボードからの標準入力の場合は非対応で終了
if sys.stdin.isatty():
    logger.info('sys.stdin.isatty is not supported')
    logger.info("end:%s" % datetime.datetime.now())
    sys.exit(0)

# 標準入力取得
msg = get_response()
if not msg:
    send_response("{response:msg_len error}")
    sys.exit(0)

# URLデコード
msg = urllib.parse.unquote(msg)

# コマンド実行
if re.search(r'{"open_in_firefox":', msg):
    msg = re.sub('}$', "", msg).split(':', 1)[1]
    match = re.match('.*firefox.exe', exe_path)
    if match:
        browser = '"' + match[0] + '" '
    else:
        logger.info("firefox not found")
        logger.info("end:%s" % datetime.datetime.now())
        sys.exit()
    cmd = browser + msg
    logger.info('run cmd:%s' % (cmd))
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res and res.stdout:
        logger.info("stdout: %s"%(res.stdout.decode('cp932')))
    if res and res.stderr:
        logger.error("stderr: %s"%(res.stderr.decode('cp932')))
elif re.search(r'"open_in_ie"', msg):
    msg = re.sub('}$', "", msg).split(':', 1)[1]
    browser = '"C:\Program Files\Internet Explorer\IEXPLORE.EXE" '
    task = "ieopen_browser_utility"
    bat = os.getcwd() + "\\" + task + ".bat"

    cmd_list = [
        'schtasks /delete /tn "' + task + '" /f',
        'schtasks /create /tn "' + task + '" /tr "' + bat + '" /sc once /sd 1900/01/01 /st 00:00',
        'schtasks /run /tn "' + task + '"',
        'schtasks /delete /tn "' + task + '" /f'
    ]

    logger.info(bat)

    with open(bat, 'w') as f:
        f.write(browser + msg)

    for cmd in cmd_list:
        logger.info(cmd)
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if res and res.stdout:
            logger.info("stdout: %s"%(res.stdout.decode('cp932')))
        if res and res.stderr:
            logger.error("stderr: %s"%(res.stderr.decode('cp932')))
else:
    logger.info("unkown request")
    logger.info("end:%s" % datetime.datetime.now())
    sys.exit()

logger.info("end:%s" % datetime.datetime.now())

send_response("{response:ok}")

