import matplotlib.pyplot as plt
import csv
import numpy as np

f = open("cpuresults.txt", "r")
data = f.readlines()
data = [float(x) for x in data]
print(data)

x = [1000, 2000, 3000, 4000, 5000]
plt.figure(figsize=(10, 7))
plt.plot(x, data)
plt.xlabel("Number of samples")
plt.ylabel("CPU Utilization (%)")
plt.show()
