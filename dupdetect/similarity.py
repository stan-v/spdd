def jaccard(set1, set2):
    return len(set1.intersection(set2)) / len(set1.union(set2))