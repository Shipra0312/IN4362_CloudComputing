from client.API import fit_predict


class KNeighborsClassifier:

    def __init__(self,  n_neighbors=5):
        self.neighbors = n_neighbors

    def __str__(self):
        return f"KNeighborsClassifier with {self.neighbors} neighbors"

    def fit_predict(self, train_x, train_y, test_x):
        fit_predict(f"KNeighborsClassifier({self.neighbors})", train_x, train_y, test_x)
