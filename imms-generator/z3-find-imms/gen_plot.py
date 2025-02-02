import matplotlib.pyplot as plt
import json

data = json.load(open('./imms-generator/solutions-16bit.json'))
x = list(map(int, data.keys()))

y = [len(v) for v in data.values()]

plt.plot(x, y)

plt.xlabel('Target Value')
plt.ylabel('Number of Instructions')
plt.title('Number of Instructions to Reach Target Value')
plt.show()