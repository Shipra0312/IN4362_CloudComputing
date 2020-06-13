import numpy as np
import csv
import matplotlib.pyplot as plt


means = []
for i in range(1, 11):
    f = open(f"latency_usersresults{i}.txt")
    data = f.readlines()
    data = list(map(lambda x: float(x), data))
    means.append(np.mean(data))

print(means)
plt.figure(figsize=(10, 7))
plt.plot(range(1, 11), means)
plt.xlabel("Number of concurrent users")
plt.ylabel("Average latency (s)")
plt.xticks(range(1, 11))
plt.title("Average latency of the system")
plt.show()
