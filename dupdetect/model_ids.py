import re

# Match all sequences of alternating alphabetic numeric that contain at least one alphabetic part followed by a numeric part.
# A numeric part may be in front and the parts may be separated by hyphens '-' or slashes '/'.
# Prevent matching a sole lowercase x which represents multiplication. 
model_id_regex = re.compile('[0-9]*[-/]?([a-wyz][a-z]*|[a-z][a-z]+)[-/]?[0-9]+.*')

def extract_model_ids(string_set) -> set:
    candidate_modelids = {s.replace('-','') for s in string_set if model_id_regex.match(s)}
    return candidate_modelids

if __name__=='__main__':
    not_model_id = {'120hz', '25"', "30inch"}
    model_id = {'tn062ab', "ec-314"}
    
    potential_modelids = extract_model_ids(not_model_id.union(model_id))
    print(potential_modelids)