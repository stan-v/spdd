from preprocessing import get_words


def is_duplicate(product1, product2, signature1, signature2, threshold, similarity, check_brand=True):
    if check_brand and 'brand' in product1 and 'brand' in product2 and product1['brand'].lower() != product2['brand'].lower():
        return (False, 'brand')
    if (signature1 == signature2).mean() >= threshold:
        return (True, 'signature')
    if similarity(get_words(product1), get_words(product2)) > threshold:
        return (True, 'similarity')
    return (False, 'similarity')


def classify(flat_products, candidates, signatures, *args, **kwargs):
    for p1, p2 in candidates:
        # pred_dupe is True/False
        pred_dupe = is_duplicate(flat_products[p1[1]], flat_products[p2[1]], signatures[:, p1[1]], signatures[:, p2[1]], *args, **kwargs)[0]
        # real_dupe = is_real_duplicate(flat_products[p1[1]], flat_products[p2[1]])

        yield (p1[1], p2[1], pred_dupe)