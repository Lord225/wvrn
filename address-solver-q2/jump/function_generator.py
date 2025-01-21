import json

# Specify the path to your JSON file
file_path = 'immediates.json'

# Open and read the JSON file
with open(file_path, 'r') as file:
    data = json.load(file)
    print("pub fn immLoadCycles(imm: u8) u8 {")
    print("\treturn switch(imm) {")
    for key, i in zip(data, range(0, 256)):
        print(f"\t\t{i} => {len(data[key])},")
    print("\t};")
    print("}")
