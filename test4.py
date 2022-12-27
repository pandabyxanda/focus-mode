#!/usr/bin/python
import time

t = (2009, 2, 17, 17, 3, 38, 1, 48, 0)
t = time.mktime(t)
print(time.strftime("%b %d %Y %H:%M:%S", time.gmtime(t)))

t = (2009, 2, 17, 12, 3, 38, 1, 48, 0)
t = time.mktime(t)
print(f"{type(t) = }")
print(time.strftime("%b %d %Y %H:%M:%S", time.gmtime(t)))

print(f"{time.gmtime() = }")

from datetime import datetime

current_date = datetime.now()
print(current_date)
print(type(current_date))
# 2022-07-14 23:37:38.578835

string_date = current_date.strftime("%Y")
print(string_date)
# 2022

import time
t = time.strftime('%H:%M:%S', time.gmtime(10))
print(f"{t = }")
# '03:25:45'