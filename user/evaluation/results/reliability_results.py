import matplotlib.pyplot as plt
import csv
import numpy as np

f = open("reliability_results_normal.txt", "r")
csv_reader = csv.reader(f, delimiter=',')
normal_data = list(csv_reader)
normal_data = [(float(x[0]), int(x[1])) for x in normal_data]
normal_data = [np.mean([float(x[0]) for x in normal_data[i*5:i*5+5]]) for i in range(5)]
print(normal_data)

f = open("reliability_results_crashed.txt", "r")
csv_reader = csv.reader(f, delimiter=',')
crashed_data = list(csv_reader)
crashed_data = [(float(x[0]), int(x[1])) for x in crashed_data]
crashed_data = [np.mean([float(x[0]) for x in crashed_data[i*5:i*5+5]]) for i in range(5)]
print(crashed_data)

x = [1000, 2000, 3000, 4000, 5000]
plt.figure(figsize=(10, 7))
plt.plot(x, normal_data)
plt.plot(x, crashed_data)
plt.xlabel("Number of samples")
plt.ylabel("Latency (s)")
plt.legend(["Normal run", "Crashed run"], loc='center left', bbox_to_anchor=(1, 0.5))

plt.show()
