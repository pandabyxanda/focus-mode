import json

# some JSON:
x =  '{ "name":"John", "age":30, "city":"New York"}'

# parse x:
y = json.loads(x)

# the result is a Python dictionary:
print(y)


# a Python object (dict):
x = {
  "name": "John",
  "age": 30,
  "city": "New York"
}

# convert into JSON:
y = json.dumps(x)
with open('j_data_file.json', 'w') as outfile:
    json.dump(x, outfile, indent=4)
# the result is a JSON string:
print(y)

with open('j_data_file.json', 'r') as outfile:
    data = json.load(outfile)

print(f"json from loaded file: {data = }")
print(type(data))
