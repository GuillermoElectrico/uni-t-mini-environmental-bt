#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## Frank@Villaro-Dixon.eu - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.
## Modified by GuillermoElectrico to add InfluxDB function

from influxdb import InfluxDBClient
from datetime import datetime
import pexpect
import time
import os
import requests

def get_measure(child):
    child.sendline("char-write-cmd 0x25 5e")
    time.sleep(.1)

    child.expect("Notification handle.*", timeout=10)
    result = child.after.split(b'\r')[0]

    value = result.decode('ascii').split('value: ')[1]
    condensed = value.replace(' ', '')
    bytemsg = bytes.fromhex(condensed)

    # For more information, look at the file
    # p004cn/com/unitrend/ienv/android/domain/service/BluetoothLeService.java
    # From the decompiled cn-com-unitrend-ienv APK application
    assert(bytemsg[4] == 0x3b)  # Uni-T UT353BT noise meter
    assert(bytemsg[14] == 0x3d)  # dB(A) units

    value = bytemsg[5:]
    value = value.split(b'=')[0]
    assert(b'dBA' in value)
    raw_value = value.split(b'dBA')[0]

    dba_noise = float(raw_value.decode('ascii'))
#    print(dba_noise)
    return dba_noise


def send_stats(stats):
#    print(stats)
    t_utc = datetime.utcnow()
    json_body = [
        {
            'measurement': 'Noise-Meter',
            'tags': {
                'id': {DEVICE},
                'meter': "UT353BT",
            },
            'time': t_utc.isoformat() + 'Z',
            'fields': {
                "dBA": stats
            }
        }
    ]

    DBclient = InfluxDBClient('127.0.0.1', '8086', 'root', 'root', 'db_unit')
    try:
        DBclient.write_points(json_body)
    except Exception as e:
        print('Data not written! in database')
        raise


DEVICE = "90:E2:02:92:E2:B4"

t_utcOn = datetime.utcnow()
t_strOn = t_utcOn.isoformat()

print('Launching gatttool -I <-> ' + t_strOn)
child = pexpect.spawn("gatttool -I")

print(f'Connecting to {DEVICE}')
child.sendline(f'connect {DEVICE}')
child.expect("Connection successful", timeout=5)
print('Connected, Hell yeah ! !')

time.sleep(1)

MaxError = 5
AcError = 0

try:
    while True:
        try:
            stats = get_measure(child)
            if AcError > 0:
                AcError = AcError - 1
        except Exception as e:
            t_utcEr1 = datetime.utcnow()
            t_strEr1 = t_utcEr1.isoformat()
            AcError = AcError + 1
            print("Sleep - Error 1 - Nº " + str(AcError) + " <-> " + t_strEr1)
#            print(e)
            if AcError > MaxError:
                break
            time.sleep(5)
        try:
            send_stats(stats)
        except Exception as e:
            t_utcEr2 = datetime.utcnow()
            t_strEr2 = t_utcEr2.isoformat()
            print("Sleep - Error 2 <-> " + t_strEr2)
#            print(e)
            time.sleep(5)
finally:
    t_utcOff = datetime.utcnow()
    t_strOff = t_utcOff.isoformat()
    child.sendline('disconnect <-> ' + t_strOff)

# vim: set ts=4 sw=4 et:

