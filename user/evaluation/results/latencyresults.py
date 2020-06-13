import numpy as np

f = open("latencyresults.txt")

data = f.readlines()
avg_data = [np.mean([float(x) for x in data[i*10:i*10+10]]) for i in range(3)]
print(avg_data)