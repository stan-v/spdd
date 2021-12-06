# Preprocessing for getting the words from the products
#
# We remove the characters from the words and replace all variants of the inch-apostrophe by '. This includes two single quotes ('') a single double quote (") and curved double quotes (”)
# We also strip any leading or trailing commas or colons.
remove_chars = '()[]&|'
strip_chars = '.,:/-'

def clean_line(line):
    return line.lower().replace('inches', 'inch').replace('-inch', 'inch').replace(' inch', 'inch').replace('inch', "'").replace('hertz', 'hz').replace(' hz', 'hz').replace(' x ', 'x')

def clean(string):
    return string.lower().translate({ord(c): None for c in remove_chars}).replace('”', "'").replace("''", "'").replace('"', "'").replace('–', '-').strip(strip_chars)

def get_words(product):
    word_set = {w for word in clean_line(product['title']).split(' ') if (w := clean(word)) not in {'amazon', 'amazon.com', 'best', 'buy', 'newegg', 'newegg.com','thenerds', 'thenerds.net', "'", '+', '-', ''}}
    return word_set
