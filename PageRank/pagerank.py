import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    print(pages)
    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    distribution = {}

    for object in corpus.keys():
        if object not in distribution.keys():
            distribution[object] = ''

    for object in corpus.keys():
        for item in corpus[object]:
            if item not in distribution.keys():
                distribution[item] = ''

    rand_probability = round((1 - damping_factor) / len(distribution.keys()), 4)

    if corpus[page]:
        link_probability = round(damping_factor / len(corpus[page]), 4)
        for object in corpus[page]:
            total = link_probability + rand_probability
            distribution[object] = round(total, 4)

    for object in distribution.keys():
        if distribution[object] == '':
            distribution[object] = rand_probability

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    ranking = {}

    list = []
    for object in corpus.keys():
        if object not in list:
            list.append(object)

    for item in list:
        if item not in ranking.keys():
            ranking[item] = 0

    first_page = random.choice(list)
    print(first_page)

    distribution = transition_model(corpus, first_page, damping_factor)
    print(distribution)

    population = []
    for object in distribution.keys():
        if object not in population:
            population.append(object)
    print('population:', population)

    weights = []
    for object in distribution.values():
        weights.append(object)
    print('weights:', weights)

    for item in ranking.keys():
        if item == first_page:
            ranking[item] = ranking[item] + 0.0001

    sample = 1

    while sample < n:
        choice = random.choices(population, weights=weights, k=1)
        page = choice[0]
        distribution = transition_model(corpus, page, damping_factor)

        weights = []
        for object in distribution.values():
            weights.append(object)

        for item in ranking.keys():
            if item == page:
                ranking[item] = ranking[item] + 0.0001
        sample = sample + 1

    return ranking


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.

    """

    distribution = {}
    page = dict()
    links = dict()

    for i in corpus:
        distribution[i] = set()

        if (len(corpus[i]) == 0):
            corpus[i] = set(corpus.keys())
    print(distribution)
    print(set(corpus.keys()))

    n = len(distribution.keys())

    for object in corpus.keys():
        for item in corpus[object]:
            distribution[item].add(object)
        links[object] = len(corpus[object])
    print(distribution)
    print(links)
    print(corpus)

    for key in corpus.keys():
        page[key] = 1 / n

    while True:
        new_page = dict()
        for item in distribution.keys():
            new_page[item] = (1 - damping_factor) / n
            for object in distribution[item]:
                new_page[item] += damping_factor * page[object]/links[object]


        active = True
        if active:
            for i in corpus:
                diff = abs(new_page[i] - page[i])
                # limit difference to .001
                if diff >= .001:
                    active = False
                # compare difference and update to sample
                page[i] = new_page[i]
            # end iteration if udner .001
            if active:
                break


    return page


if __name__ == "__main__":
    main()
