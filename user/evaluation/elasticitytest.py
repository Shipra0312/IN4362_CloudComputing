from server.KNeighborsClassifier import KNeighborsClassifier
from sklearn.datasets import make_blobs
from sklearn.model_selection import train_test_split
import numpy as np
import threading
import time
import random


def main():
    for i in range(10):
        time.sleep(random.randint(2, 6))
        thread = threading.Thread(target=run)
        thread.start()


def run():
    clf = KNeighborsClassifier(3)
    X, y = make_blobs(n_samples=3000, centers=2, n_features=5, random_state=42)
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    outcome = clf.fit_predict(x_train, y_train, x_test)
    error_amount = np.sum(np.abs(outcome - y_test))
    print(error_amount)


main()
