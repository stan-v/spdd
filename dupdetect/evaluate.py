import numpy as np

def obs_type(prediction, actual):
    if actual is np.nan:
        return 'unknown'
    if prediction and actual:
        return 'TP'
    if prediction and not actual:
        return 'FP'
    if not prediction and actual:
        return 'FN'
    if not prediction and not actual:
        return 'TN'

def is_real_duplicate(product1, product2):
    return product1['modelID'] == product2['modelID'] if product1['modelID'] is not None else np.nan


def real_labels(flat_products, candidates):
    for p1, p2 in candidates:
        real_dupe = is_real_duplicate(flat_products[p1[1]], flat_products[p2[1]])

        yield (p1[1], p2[1], real_dupe)

def grade_classification(flat_products, classification):
    for i1, i2, pred in classification:
        real_dupe = is_real_duplicate(flat_products[i1], flat_products[i2])
        yield (i1, i2, obs_type(pred, real_dupe))

def confusion_matrix(graded_classification, num_real_duplicates, num_products):
    confusion = {'TP': 0, 'FP': 0, 'TN': 0, 'FN': 0, 'unknown': 0, 'num_comparisons': len(graded_classification)}
    total = num_products * (num_products-1) / 2
    for p1, p2, c in graded_classification:
        if c == 'TP':
            confusion['TP'] += 1
        elif c == 'FP':
            confusion['FP'] += 1
        elif c == 'unknown':
            confusion['unknown'] += 1
    
    confusion['FN'] = int(num_real_duplicates - confusion['TP'])
    confusion['TN'] = int(total - num_real_duplicates - confusion['FP'])
    return confusion

def pair_performance(graded_classification, num_real_duplicates):
    num_comparisons = len(graded_classification)
    Df = sum([1 if c == 'TP' or c == 'FN' else 0 for i1, i2, c in graded_classification])
    return {'PQ': Df/num_comparisons, 'PC': Df/num_real_duplicates}


def plot_confusion(confusion, num_real_duplicates, num_products):
    t = num_products * (num_products-1) / 2
    print("""Confusion Matrix:
Actual / Pred. |     True     |     False    | Total
---------------|--------------|--------------|-------------
          True | TP = {TP:^8}| FN = {FN:^8}| w = {w}
         False | FP = {FP:^8}| TN = {TN:^8}| s = {s}
---------------|--------------|--------------|-------------
         Total |  c = {c:^8}|  f = {f:^8}| t = {t}
    
    """.format(**confusion, c=confusion['TP'] + confusion['FP'], f=confusion['TN'] + confusion['FN'], w=num_real_duplicates, t=t, s=t-num_real_duplicates))

def evaluate(TP=0, FP=0, TN=0, FN=0, unknown=0, PC=0, PQ=0, num_real_duplicates=0, num_comparisons=0, num_products=0):

    assert TP + FP + TN + FN == num_products * (num_products-1) / 2 
    num_all_comparison = num_products * (num_products-1) / 2 

    precision = TP / (TP + FP)
    recall = TP / (TP + FN)

    if TP == 0:
        F1 = 0
        F1_star = 0
    else:
        F1 = 2 * precision * recall / (precision + recall)
        F1_star = 2 * PQ * PC / (PQ + PC)
    return {'precision': precision, 'recall': recall, 'F1': F1, 
            'PQ': PQ, 'PC': PC, 'F1*': F1_star, 
            'num_comparisons': num_comparisons,
            'proportion_comparisons': num_comparisons/num_all_comparison}


