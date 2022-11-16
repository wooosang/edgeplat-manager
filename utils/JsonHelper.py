import json

data = None
# Read Existing JSON File
with open('conf/0_config.json') as f:
    data = json.load(f)
    print(data["area"][0]['name'])
    print(data["area"][0]['matchFuction']['ncc_standScore'])
    data["area"][0]['matchFuction']['ncc_standScore'] = "0.7"

with open('conf/0_config2.json', 'w') as f:
    json.dump(data, f, indent=2)