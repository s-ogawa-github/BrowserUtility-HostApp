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

def get_foregroundapp_path():
    # 実行ファイル取
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(ctypes.windll.user32.GetForegroundWindow(), ctypes.pointer(pid))
    cmd = 'wmic process where "processid = ' + str(pid.value) + '" get ExecutablePath'
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res and res.stdout:
        res = res.stdout.decode('cp932').split('\r\n')
        if len(res) >= 2:
            return res[1]

    logger.info('ExecutablePath not found: pid=%d', pid.value)
    logger.info("end:%s" % datetime.datetime.now())
    return None

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

# キーボードからの標準入力の場合は非対応で終了
if sys.stdin.isatty():
    logger.info('sys.stdin.isatty is not supported')
    logger.info("end:%s" % datetime.datetime.now())
    send_response("{response:ng}")
    sys.exit()

# 標準入力取得&URLデコード
get_stdin = get_response()
if not get_stdin:
    send_response("{response:msg_len error}")
    sys.exit()
msg = json.loads(get_stdin)

logger.info(get_stdin)
version = msg.get('version')
mode = msg.get('mode')
if not version or not mode:
    logger.info("recieved message is not supported: %s", res_msg)
    logger.info("end:%s" % datetime.datetime.now())
    send_response("{response:ng}")
    sys.exit()

# コマンド実行
if mode == "open_in_firefox":
    path = msg.get('path')
    if not path:
        logger.info("mode:%s path is not found: %s", mode, res_msg)
        logger.info("end:%s" % datetime.datetime.now())
        send_response("{response:ng}")
        sys.exit()

    match = re.match('.*firefox.exe', get_foregroundapp_path())
    if match:
        browser = '"' + match[0] + '" '
    else:
        logger.info("firefox not found")
        logger.info("end:%s" % datetime.datetime.now())
        send_response("{response:ng}")
        sys.exit()

    cmd = browser + '"' + urllib.parse.unquote(path) + '"'
    logger.info('run cmd:%s' % (cmd))
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res and res.stdout:
        logger.info("stdout: %s"%(res.stdout.decode('cp932')))
    if res and res.stderr:
        logger.error("stderr: %s"%(res.stderr.decode('cp932')))

elif mode == "open_in_ie":
    path = msg.get('path')
    if not path:
        logger.info("mode:%s path is not found: %s", mode, res_msg)
        logger.info("end:%s" % datetime.datetime.now())
        send_response("{response:ng}")
        sys.exit()

    cmd = os.getcwd() + "\\ieopen_browser_utility.vbs"
    with open(cmd, 'w') as f:
        f.write('Option Explicit\n')
        f.write('Dim IE\n')
        f.write('set IE = CreateObject ("InternetExplorer.Application")\n')
        f.write('IE.Visible = True\n')
        f.write('IE.Navigate "' + urllib.parse.unquote(path) + '"\n')
        f.write('Do While IE.Busy\n')
        f.write('  WScript.Sleep 100\n')
        f.write('Loop\n')
        f.write('Set IE = Nothing\n')

    logger.info('run cmd:%s' % (cmd))
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res and res.stdout:
        logger.info("stdout: %s"%(res.stdout.decode('cp932')))
    if res and res.stderr:
        logger.error("stderr: %s"%(res.stderr.decode('cp932')))

else:
    logger.info("unkown request")
    logger.info("end:%s" % datetime.datetime.now())
    send_response("{response:ng}")
    sys.exit()

logger.info("end:%s" % datetime.datetime.now())

send_response("{response:ok}")
