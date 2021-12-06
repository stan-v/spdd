from model_ids import extract_model_ids

def lsh(signature, r=5, b=20):
    """
    Maps a signature to b different 'buckets' using Locality Sensitive Hashing.
    :param signature: A signature, list of length n with integers (obtained from minhashing, where n is the number of permutations used for minhashing)
    :param b: Number of bands, this is the different number of buckets a signature is hashed to
    :param r: The size of a band, this is implied by N/b. 
    The hashing to a bucket is done via a dict object. The integers are concatenated as strings to form the hash string. They are prefixed with the band number and a hyphen
    to prevent other bands with the same sequence of minhash values to map to the same bucket. This means that every band maps to its own set of buckets, such that bands
    at different positions in the signature for two signatures do not hash to the same bucket. 
    The hash string is the identifier of the bucket the signature is hashed to. 
    """
    assert r*b == len(signature)
    bands = [signature[i*r:(i+1)*r] for i in range(b)]  # Split into bands
    buckets = {str(b)+ '-' + ''.join([str(int(s)) for s in band]) for b, band in enumerate(bands)}
    return buckets


def model_buckets(product_set):
    """
    Obtain the additional buckets to map to
    """
    return extract_model_ids(product_set)

    
def add_to_buckets(buckets, signature, product_index, bs):
    """
    Hash to buckets
    r and b are determined in the previous cell
    r = Number of signature rows per band
    b = Number of bands
    ! b times r must be equal to n
    """

    new_element = (''.join([str(int(s)) for s in signature]), product_index)
    for bucket in bs:
        if bucket in buckets:
            buckets[bucket].append(new_element)
        else:
            buckets[bucket] = [new_element]