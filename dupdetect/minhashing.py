from itertools import product
import numpy as np

from preprocessing import get_words


# Find the optimal value for r and b given the desired similarity
left = 0
right = 1

def a(s, r, b):
    """
    Evaluate the probability of being a candidate: Pr[similar in at least 1 band] = 1 - Pr[Not similary in all bands]
    """
    return 1 - (1-s**r)**b

def search(fn, opt, left, right, epsilon=0.00001):
    """
    Binary search over a monotonically increasing function fn.
    Searches for the argument of fn(x) that minimizes |fn(x) - opt| 

    Returns (x*, fn(x*), fn(x*) - opt)
    """
    
    x = (left+right)/2
    val = fn(x)
    err = val-opt
    while abs(err) >= epsilon:
        if val < opt:
            left = x
        else:
            right = x
        x = (left+right)/2
        val = fn(x)
        err = val-opt
    return x, val, err

def possible_bands(n):
    options = []

    pairs = [(int(n/b), b)for b in range(1, n+1) if n % b == 0]  # Construct pairs of (r,b) that are possible with the given n. 
    for (r,b) in pairs:
        s = search(lambda s: a(s,r,b)-0.5, 0, 0, 1) # Find the threshold
        options.append((r,b, s[0]))  # Record pair and threshold
    return options

def best_bands(desired_sim, n):
    """
    Find the tuple (r,b) that has the threshold closest to desired_sim as possible. Only pairs of (r,b) are considered
    where both r and b are integer and where r x b = n. 
    """
    opt_s = possible_bands(n)

    best = min(opt_s, key=lambda option: abs(option[2] - desired_sim)) # Find pair with threshold closest to desired similarity.
    return best

def isprime(number):
    for i in range(2, int(number**0.5)+1):
        if number % i == 0:
            return False, i
    return True


def generate_minhash_funcs(num_const, num_mult, R):

    const = np.linspace(0, (num_const-1)/num_const*R, num_const, dtype=int)
    mult = np.linspace(int(R/num_mult), R-1, num_mult, dtype=int)
    hash_funcs = product(const, mult)  # This is a generator, be careful about multiple iterations!
    return hash_funcs


def make_signatures(word_set, product_sets, hash_funcs, n, R):
    M = np.ones((n, len(product_sets))) * np.inf  # M is the signature matrix of n x p (n = # hashfunctions, p = number of products)
    h_i = np.zeros(n)
    for (row, w) in enumerate(word_set): 
        for h, (const, mult) in enumerate(hash_funcs): # Obtain the hash function parameters           
            h_i[h] = (const + mult * (row+1)) % R # Maps the row to the permutation 
            assert h_i[h] < np.inf
        for h, perm_row in enumerate(h_i):
            for index, product_set in enumerate(product_sets):
                if w in product_set:
                    M[h, index] = min(M[h,index], perm_row)
    return M

def precompute_signatures(data, num_const=105, num_mult=11, R=2*3*5*7*11*13*17+19, *args, **kwargs):
    products = [product for products in list(data.values()) for product in products]

    all_words = sorted({word for product in products for word in get_words(product)})
    product_sets = [get_words(product) for product in products]

    assert isprime(R)

    hash_funcs = list(generate_minhash_funcs(num_const, num_mult, R))
    
    return make_signatures(all_words, product_sets, hash_funcs, len(hash_funcs), R)
