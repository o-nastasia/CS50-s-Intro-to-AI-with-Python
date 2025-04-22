import csv
import sys


from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []
    data = evidence, labels

    with open(filename) as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Revenue"] == "TRUE":
                labels.append(1)
            else:
                labels.append(0)

            if row["VisitorType"] == "Returning_Visitor":
                row["VisitorType"] = int(1)
            else:
                row["VisitorType"] = int(0)
            if row["Weekend"] == "TRUE":
                row["Weekend"] = 1
            if row["Weekend"] == "FALSE":
                row["Weekend"] = 0
            if row["Month"] == "Jan":
                row["Month"] = 0
            if row["Month"] == "Feb":
                row["Month"] = 1
            if row["Month"] == "Mar":
                row["Month"] = 2
            if row["Month"] == "Apr":
                row["Month"] = 3
            if row["Month"] == "May":
                row["Month"] = 4
            if row["Month"] == "June":
                row["Month"] = 5
            if row["Month"] == "Jul":
                row["Month"] = 6
            if row["Month"] == "Aug":
                row["Month"] = 7
            if row["Month"] == "Sep":
                row["Month"] = 8
            if row["Month"] == "Oct":
                row["Month"] = 9
            if row["Month"] == "Nov":
                row["Month"] = 10
            if row["Month"] == "Dec":
                row["Month"] = 11

            evidence.append([int(row["Administrative"]), float(row["Administrative_Duration"]), int(row["Informational"]),
                            float(row["Informational_Duration"]), int(
                                row["ProductRelated"]), float(row["ProductRelated_Duration"]),
                            float(row["BounceRates"]), float(row["ExitRates"]), float(
                                row["PageValues"]), float(row["SpecialDay"]),
                            int(row["Month"]), int(row["OperatingSystems"]), int(
                                row["Browser"]), int(row["Region"]), int(row["TrafficType"]),
                            int(row["VisitorType"]), int(row["Weekend"])])

    return data


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    model = KNeighborsClassifier(n_neighbors=1)

    X = evidence
    y = labels
    model.fit(X, y)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    n = 0
    sen = 0
    pos = 0
    spec = 0
    neg = 0

    while n < len(labels) and n < len(predictions):
        if labels[n] == 1:
            pos = pos + 1
        if labels[n] == 0:
            neg = neg + 1
        if labels[n] == predictions[n] and labels[n] == 1:
            sen = sen + 1
        if labels[n] == predictions[n] and labels[n] == 0:
            spec = spec + 1
        n = n + 1

    sensitivity = sen / pos
    specificity = spec / neg
    result = sensitivity, specificity

    return result


if __name__ == "__main__":
    main()
