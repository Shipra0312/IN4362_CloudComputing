from client.KNeighborsClassifier import KNeighborsClassifier


def main():
    clf = KNeighborsClassifier(1)
    clf.fit_predict([[0, 2, 0], [2, 3, 4]], [0, 1], [[0, 1, 0], [1, 2, 3]])


main()
