#!/usr/bin/python3

import argparse
import os

# error messages
INVALID_FILETYPE_MSG = "Error: Invalid file format. {} must be a .txt file."
INVALID_PATH_MSG = "Error: Invalid file path/name. Path {} does not exist."
  
  
def validate_file(file_name):
    '''
    validate file name and path.
    '''
    if not valid_path(file_name):
        print(INVALID_PATH_MSG.format(file_name))
        quit()
    elif not valid_filetype(file_name):
        print(INVALID_FILETYPE_MSG.format(file_name))
        quit()
    return
      
def valid_filetype(file_name):
    # validate file type
    return file_name.endswith('.json')
  
def valid_path(path):
    # validate file path
    return os.path.exists(path)

def main():
    parser = argparse.ArgumentParser(description='Product duplicate detection program.')

    parser.add_argument('file', nargs=1, metavar='FILE', type=str, help='A JSON file containing all the products indexed by their model IDs')

    parser.add_argument('--train', action='store_true', help='Train the algorithm using 5 bootstraps.')
    parser.add_argument('--test', nargs=1, type=str, metavar='TRAIN_DIR', help='Test on out-of-bag bootstrap samples using result from bootstrap optimization. TRAIN_DIR is the directory containing bootstrap-i-results.json. This is usually the results/ directory.')
    parser.add_argument('-s', '--sim', nargs=1, metavar='SIM', type=float, help='Threshold similarity for classifying as duplicate. Default: 0.999')
    args = parser.parse_args()

    if args.file != None:
        validate_file(args.file[0])
        import json
        data = json.load(open(args.file[0], 'r'))
        if args.train:
            from optimize import train
            print('Training on bootstraps from: ' + args.file[0])
            train(data)
        elif args.test:
            from optimize import test
            print('Testing on out-of-bag sample from: ' + args.file[0])
            test(data, None, load_from_dir=args.test[0])
        else:
            from detect import detect
            
            kwargs = {'desired_similarity': args.sim[0]} if args.sim else {}
            print('Performing duplicate detection on file: ' + args.file[0])
            detect(data, **kwargs)
    
if __name__=='__main__':
    main()
