import os
import json
import random

import numpy as np
from detect import detect
from minhashing import precompute_signatures, possible_bands

random.seed(123)


def bootstrap_from_file(file, *args, **kwargs):
    """Wrapper for the bootstrap method. Loads file and feeds the data to the bootstrapper."""
    data = json.load(open(file, 'r'))
    return bootstrap(data, *args, **kwargs)

def bootstrap(data):
    # Unpack products
    products = [product for products in list(data.values()) for product in products]
    # Select part of the products
    # bootstrap = random.choices(products, k=len(products))
    # Only use doubly-samples products once!
    bootstrap_indices = np.unique(np.random.randint(low=0, high=len(products), size=len(products)))
    bootstrap = [products[k] for k in bootstrap_indices]

    # Obtain out of bag products
    out_of_bag = [p for p in products if p not in bootstrap]

    # Convert to dictionaries in the original data format
    bootstrap_dict = {}
    for p in bootstrap:
        mid = p['modelID']
        if mid in bootstrap_dict:
            bootstrap_dict[mid].append(p)
        else:
            bootstrap_dict[mid] = [p]

    out_of_bag_dict = {}
    for p in out_of_bag:
        mid = p['modelID']
        if mid in out_of_bag_dict:
            out_of_bag_dict[mid].append(p)
        else:
            out_of_bag_dict[mid] = [p]

    return (bootstrap_dict, out_of_bag_dict)


def train(data):
    random.seed(123)

    # Initialize list of (bootstrap, out-of-bag) samples
    boots = []

    boot_results = []

    for n_bootstrap in range(1, 6): # Perform 5 bootstraps

        print('Bootstrap: {}\n'.format(n_bootstrap))
        # Draw bootstraps 
        bootstrap_dict, out_of_bag_dict = bootstrap(data)
        boots.append((bootstrap_dict, out_of_bag_dict))

        # Pre-compute signature to save CPU time
        pre_comp_signature = precompute_signatures(bootstrap_dict)
        
        # Ensure the proper directories are created
        cache_f = 'cache/signature-bootstrap-{}.npy'.format(n_bootstrap)
        os.makedirs(os.path.dirname(cache_f), exist_ok=True)
        os.makedirs('results', exist_ok=True)
        np.save(cache_f, pre_comp_signature)

        # Perform optimization
        results = []
        n = 1155
        for (r,b,threshold) in possible_bands(n):
            for compare_sim in np.linspace(0, 1, 11):  # Optimize over compare_sim, given a lsh_sim. 

                performance = detect(bootstrap_dict, lsh_similarity=threshold, compare_similarity=compare_sim,pre_comp_signature=pre_comp_signature)
                results.append((r,b,threshold, performance, compare_sim))


        json.dump(results, open('results/bootstrap-{}-results.json'.format(n_bootstrap), 'w'))
        boot_results.append(results)
    return boot_results


def test(data, boot_results, optimality_metric='F1', load_from_dir=None):
    random.seed(123)

    # Initialize list of (bootstrap, out-of-bag) samples
    boots = []
    eval_results = []


    for n_bootstrap in range(1, 6): # Perform 5 bootstraps

        print('Bootstrap: {}\n'.format(n_bootstrap))
        # Draw bootstraps 
        bootstrap_dict, out_of_bag_dict = bootstrap(data)
        boots.append((bootstrap_dict, out_of_bag_dict))

        if load_from_dir is not None:
            boot_results = json.load(open(load_from_dir + '/bootstrap-{}-results.json'.format(n_bootstrap), 'r'))

        n = 1155
        for (r,b,threshold) in possible_bands(n):

            # Perform optimization
            best_setting_index = np.argmax([r[3][optimality_metric] for r in boot_results if r[2] == threshold])
            best_settings = [r for r in boot_results if r[2] == threshold][best_setting_index]
            eval = detect(out_of_bag_dict, lsh_similarity=threshold, compare_similarity=best_settings[4])
            eval_results.append((*best_settings[0:3], best_settings[4], eval))
 
    os.makedirs('results', exist_ok=True)
    json.dump(eval_results, open('results/oob-results.json', 'w'))
    for (r,b,threshold) in possible_bands(n):
        print('Average Performance for lsh_similarity {}:\n'.format(threshold))
        avg_perf = average_performance(eval_results, threshold)
        print('\n'.join(['{:>22}: {}'.format(k,v) for k, v in avg_perf.items()]))
    return eval_results

def average_performance(eval_results, lsh_similarity):
    # Map to performance metrics
    eval_performances = [r[4] for r in eval_results if r[2] == lsh_similarity]
    # Group-by metric and average
    averages = {k: sum(vs := [p[k] for p in eval_performances])/len(vs) for k in eval_performances[0].keys() }
    return averages
    



