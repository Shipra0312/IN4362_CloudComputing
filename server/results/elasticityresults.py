import matplotlib.pyplot as plt
import csv
import numpy as np

f = open("elasticityresults.txt", "r")
csv_reader = csv.reader(f, delimiter=',')
data = list(csv_reader)
data = [[int(x[0]), int(x[1]), int(x[2])] for x in data]
data = np.array(data)

x = 2*np.arange(len(data))
plt.figure(figsize=(10,7))
plt.plot(x, data[:,0])
plt.plot(x, data[:,1])
plt.plot(x, data[:,2])
plt.legend(["Total instances", "Running instances", "Users"], loc='center left', bbox_to_anchor=(1, 0.5))
plt.xlabel("Time (s)")
plt.title("System Elasticity for multiple users")
plt.show()
f.close()
