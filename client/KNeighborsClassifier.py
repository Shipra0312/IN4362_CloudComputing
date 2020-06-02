from client.API import fit_predict
import numpy as np


class KNeighborsClassifier:

    def __init__(self,  n_neighbors=5):
        self.neighbors = n_neighbors

    def __str__(self):
        return f"KNeighborsClassifier with {self.neighbors} neighbors"

    def fit_predict(self, X_train, y_train, X_test):
        output = fit_predict(f"KNeighborsClassifier({self.neighbors})", X_train, y_train, X_test)
        output = output.replace("[", "").replace("]", "")
        output = np.fromstring(output, dtype=int, sep=' ')
        return output
