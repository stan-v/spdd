# Python native imports
import json
from itertools import combinations

# Internal package imports
from preprocessing import clean, clean_line, get_words
from model_ids import extract_model_ids

from minhashing import best_bands, isprime, generate_minhash_funcs, make_signatures

from similarity import jaccard

from lsh import add_to_buckets, lsh, model_buckets
from compare import classify
from evaluate import plot_confusion, confusion_matrix, grade_classification, evaluate, pair_performance

def detect_from_file(file, *args, **kwargs):
    data = json.load(open(file, 'r'))
    return detect(data, *args, **kwargs)


def detect(data, compare_similarity=0.999, lsh_similarity=0.999, num_const = 105, num_mult = 11, pre_comp_signature=None):

    modelIDs = list(data.keys())

    products = [product for products in list(data.values()) for product in products]
    
    flat_products = [{**{clean(k).replace('brand name', 'brand'): clean_line(v) for k, v in product['featuresMap'].items()}, 
                'title': clean_line(product['title']),
                'shop': product['shop'].lower(),
                'url': product['url'],
                'modelID': product['modelID'] if 'modelID' in product else None} for product in products]

    # Obtain data statistics
    # Obtain number of duplicates per modelID
    num_products = len(flat_products)

    real_duplicate_pairs = [(product1, product2) for modelID, same_prods in data.items() for product1, product2 in combinations(same_prods, 2)]

    data_stats = {'n': num_products, 'Nd': len(real_duplicate_pairs)}
    print("Data statistics: ", data_stats)

    # Obtain all words in every product
    all_words = sorted({word for product in products for word in get_words(product)})

    # Obtain the feature matrix (in a sparse way) Every product has a set of words from the all words set.
    product_sets = [get_words(product) for product in products]

    # Find the best values of r and b given n
    n = 3*5*7*11  # Number of minhash functions (1155)

    (r, b, threshold) = best_bands(lsh_similarity, n)
    print('r: {} - b: {} - threshold: {}'.format(r, b, threshold))

    # Minhash functions 
    R = 2*3*5*7*11*13*17+19

    print('Using modulus for minhash functions: R = {}, R is prime: {}'.format(R, isprime(R)))

    # Generate the actual minhash functions given the bands and row
    print('Using {} multipliers and {} shifts'.format(num_mult, num_const))
    hash_funcs = list(generate_minhash_funcs(num_const, num_mult, R))

    if pre_comp_signature is None:
        signatures = make_signatures(all_words, product_sets, hash_funcs, len(hash_funcs), R)
    else:
        signatures = pre_comp_signature
    

    # Perform the LSH-ing
    buckets = {}
    mid_buckets = {}
    for index in range(signatures.shape[1]): # For all signatures (which are columns in the signature matrix)
        sgn = signatures[:, index]
        product_set = product_sets[index]

        add_to_buckets(mid_buckets, sgn, index, model_buckets(product_set))
        add_to_buckets(buckets, sgn, index, lsh(sgn, r=r, b=b))
    
    # Discard all buckets with less than 2 entities
    # bucket_sizes = [len(b_prods) for k, b_prods in buckets.items()]
    filled_buckets = {k: b_prod for k, b_prod in buckets.items() if len(b_prod) >= 2}

    # mid_bucket_sizes = [[len(b_prods) for k, b_prods in mid_buckets.items()]]
    mid_filled_buckets = {k: b_prod for k, b_prod in mid_buckets.items() if len(b_prod) >= 2}

    print('Reduced amount of buckets from {} to {}'.format(len(buckets), len(filled_buckets)))
    print('Reduced amount of model ID buckets from {} to {}'.format(len(mid_buckets), len(mid_filled_buckets)))


    # Generate candidates from all buckets
    
    mid_candidates = {(p1, p2) for k in mid_filled_buckets.keys() for p1, p2 in combinations(mid_filled_buckets[k], 2)} # p1 = (signature, index), p2 = (signature, index)
    print('Number of model ID candidates: {}'.format(len(mid_candidates)))
    candidates = {(p1, p2) for k, b_prods in filled_buckets.items() for p1, p2 in combinations(b_prods,2) if (p1, p2) not in mid_candidates}
    len(candidates)
    print('Number of regular candidates: {}'.format(len(candidates)))

    print('Using Jaccard similarity with threshold: {}'.format(compare_similarity))
    # Classify everything and compute performance measures
    classification = [*classify(flat_products, candidates, signatures, compare_similarity, jaccard), *classify(flat_products, mid_candidates, signatures, 0.0, jaccard, check_brand=False)]
    # classification = [*classify(flat_products, candidates, signatures, 0.6, jaccard, check_brand=False)]


    conf_mat = confusion_matrix(list(grade_classification(flat_products, classification)), data_stats['Nd'])
    print() # Print newline
    plot_confusion(conf_mat, data_stats['Nd'], data_stats['n'])

    performance = evaluate(**conf_mat, num_real_duplicates=data_stats['Nd'])
    print('\n'.join(['{:>22}: {}'.format(k,v) for k, v in performance.items()]))

    print('DONE')
    return performance

if __name__=='__main__':
    detect_from_file('data/data.json')