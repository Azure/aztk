from __future__ import print_function
import sys

def memory_info():
    res = {}
    for row in open('/proc/meminfo', 'r'):
        k, v = row.split(':')
        k = k.strip()
        v = v.split()
        if len(v) == 1:
            v = int(v[0])
        elif v[1] == 'kB':
            v = int(v[0]) / 1024
        elif v[1] == 'mB':
            v = int(v[0]) / 1024 / 1024
        res[k] = v
    return res

if __name__ == "__main__":
    x = memory_info()
    print('{} GB', x['MemAvailable'])
    print('Set to 75% = {}', x['MemAvailable'] * 0.75)
    print(x)



