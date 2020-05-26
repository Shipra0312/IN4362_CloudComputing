from client.KNeighborsClassifier import KNeighborsClassifier


def main():
    clf = KNeighborsClassifier(3)
    clf.fit_predict([1, 2, 3], [0, 1, 0], [2, 3, 4])


main()
