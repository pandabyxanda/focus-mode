import json

x = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
res = {k: v for k, v in sorted(x.items(), key=lambda item: item[1])}
# {0: 0, 2: 1, 1: 2, 4: 3, 3: 4}
print(res)

try:
    with open('data_file.json', 'r') as outfile:
        apps = json.load(outfile)
except:
    sapps = {}

print(apps)
res = {k: v for k, v in sorted(apps.items(), key=lambda item: item[1]['time'], reverse=True)}
print(res)