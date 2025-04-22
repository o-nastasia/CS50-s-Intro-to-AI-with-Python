import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    probs = []

    for person in people:
        if people[person]['mother'] == None and people[person]['father'] == None:
            if person in one_gene:
                probs.append(PROBS["gene"][1])
                if person in have_trait:
                    probs.append(PROBS["trait"][1][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][1][False])
            if person in two_genes:
                probs.append(PROBS["gene"][2])
                if person in have_trait:
                    probs.append(PROBS["trait"][2][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][2][False])
            if person not in one_gene and person not in two_genes:
                probs.append(PROBS["gene"][0])
                if person in have_trait:
                    probs.append(PROBS["trait"][0][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][0][False])

        if people[person]['mother'] and people[person]['father']:
            if people[person]["father"] in two_genes:
                probability_father = 1 - PROBS["mutation"]
                probability_not_father = PROBS["mutation"]
            if people[person]["mother"] in two_genes:
                probability_mother = 1 - PROBS["mutation"]
                probability_not_mother = PROBS["mutation"]

            if people[person]["father"] not in two_genes and people[person]["father"] not in one_gene:
                probability_father = PROBS["mutation"]
                probability_not_father = 1 - PROBS["mutation"]
            if people[person]["mother"] not in two_genes and people[person]["mother"] not in one_gene:
                probability_mother = PROBS["mutation"]
                probability_not_mother = 1 - PROBS["mutation"]

            if people[person]["father"] in one_gene:
                probability_father = 0.5
                probability_not_father = 0.5
            if people[person]["mother"] in one_gene:
                probability_mother = 0.5
                probability_not_mother = 0.5

            if person in one_gene:
                total = probability_father*probability_not_mother + probability_mother*probability_not_father
                if person in have_trait:
                    probs.append(PROBS["trait"][1][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][1][False])
            if person in two_genes:
                total = probability_mother * probability_father
                if person in have_trait:
                    probs.append(PROBS["trait"][2][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][2][False])
            if person not in one_gene and person not in two_genes:
                total = probability_not_mother * probability_not_father
                if person in have_trait:
                    probs.append(PROBS["trait"][0][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][0][False])

            probs.append(total)

        if people[person]['mother'] and not people[person]['father']:
            probability_father = 0.5
            probability_not_father = 0.5

            if people[person]["mother"] in two_genes:
                probability_mother = 1 - PROBS["mutation"]
                probability_not_mother = PROBS["mutation"]

            if people[person]["mother"] not in two_genes and people[person]["mother"] not in one_gene:
                probability_mother = PROBS["mutation"]
                probability_not_mother = 1 - PROBS["mutation"]

            if people[person]["mother"] in one_gene:
                probability_mother = 0.5
                probability_not_mother = 0.5

            if person in one_gene:
                total = probability_father*probability_not_mother + probability_mother*probability_not_father
                if person in have_trait:
                    probs.append(PROBS["trait"][1][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][1][False])
            if person in two_genes:
                total = probability_mother * probability_father
                if person in have_trait:
                    probs.append(PROBS["trait"][2][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][2][False])
            if person not in one_gene and person not in two_genes:
                total = probability_not_mother * probability_not_father
                if person in have_trait:
                    probs.append(PROBS["trait"][0][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][0][False])

            probs.append(total)

        if people[person]['father'] and not people[person]['mother']:
            probability_mother = 0.5
            probability_not_mother = 0.5

            if people[person]["father"] in two_genes:
                probability_father = 1 - PROBS["mutation"]
                probability_not_father = PROBS["mutation"]

            if people[person]["father"] not in two_genes and people[person]["father"] not in one_gene:
                probability_father = PROBS["mutation"]
                probability_not_father = 1 - PROBS["mutation"]

            if people[person]["father"] in one_gene:
                probability_father = 0.5
                probability_not_father = 0.5

            if person in one_gene:
                total = probability_father*probability_not_mother + probability_mother*probability_not_father
                if person in have_trait:
                    probs.append(PROBS["trait"][1][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][1][False])
            if person in two_genes:
                total = probability_mother * probability_father
                if person in have_trait:
                    probs.append(PROBS["trait"][2][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][2][False])
            if person not in one_gene and person not in two_genes:
                total = probability_not_mother * probability_not_father
                if person in have_trait:
                    probs.append(PROBS["trait"][0][True])
                elif person not in have_trait:
                    probs.append(PROBS["trait"][0][False])

            probs.append(total)

    joint = 1
    for number in probs:
        joint *= number
    return (joint)


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for name in probabilities:
        if name in one_gene:
            probabilities[name]['gene'][1] += p
        if name in two_genes:
            probabilities[name]['gene'][2] += p
        if name in have_trait:
            probabilities[name]['trait'][True] += p
        if name not in one_gene and name not in two_genes:
            probabilities[name]['gene'][0] += p
        if name not in have_trait:
            probabilities[name]['trait'][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for name in probabilities:
        gene_2 = probabilities[name]['gene'][2]
        gene_1 = probabilities[name]['gene'][1]
        gene_0 = probabilities[name]['gene'][0]
        normalize = gene_2 + gene_1 + gene_0
        probabilities[name]['gene'][2] = round((gene_2 / normalize), 4)
        probabilities[name]['gene'][1] = round((gene_1 / normalize), 4)
        probabilities[name]['gene'][0] = round((gene_0 / normalize), 4)

        trait_true = probabilities[name]['trait'][True]
        trait_false = probabilities[name]['trait'][False]
        normalize = trait_true + trait_false
        probabilities[name]['trait'][True] = round((trait_true / normalize), 4)
        probabilities[name]['trait'][False] = round((trait_false / normalize), 4)


if __name__ == "__main__":
    main()
