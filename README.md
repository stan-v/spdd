# Scalable Product Duplicate Detection
### Author: Stan Verstappen

![spdd_logo](https://user-images.githubusercontent.com/33269018/144854214-7832b6ac-e273-4751-b497-23c3bcd981b3.png)

This repository is an implementation of the Locality Sensitive Hashing algorithm for application in product duplicate detection.

-----------------
[![python_version](https://img.shields.io/badge/python-v3.8%2B-green?logo=python)](https://python.org)
![requirements](https://img.shields.io/badge/requires-numpy-green)
## Features:
The application by default reads a JSON file with the annotated modelIDs and performs the classification task and evaluates the performance on the entire dataset given in the file argument. Alternative modes are available for training and testing the duplicate detecting algorithm using bootstrapping.

## Requirements:
 - Python >= 3.8
 - numpy

## Installation:
Using Git:

`git clone https://github.com/stan-v/spdd.git`

Manually:
Press the green 'Code' button and click Download ZIP. Extract the zip-file and open the spdd folder.


## Usage
Make sure you have installed the above requirements.
The program can be run in different modes. In the following `python` should refer to a python executable with version 3.8 or higher. This may mean that it has to be replaced by `python3`, `python3.8` or `/some/path/to/python` (linux) or `C:\Some\Path\To\python.exe` (Windows) depending on where your python interpreter is located. 

Mode 1: classify and evaluate 1 file with defaults:
Open your preferred command line and run the command within the spdd project folder:
```bash
python dupdetect FILE
``` 
where FILE points to a valid JSON file containing the products you want to analyse. 
The optional argument `--sim SIM` can change the desired similarity for classification, for example 
`python dupdetect --sim 0.999 data/data.json`, will classify using this similarity as threshold value.
The optional argument `--lsh-sim LSH_SIM` can change the choice of bands used by the LSH algorithm. The bands will be picked to as closely match the threshold value to LSH_SIM. 

Mode 2: train on bootstraps from a file:
```bash
python dupdetect --train FILE
``` 
Mode 3: test on out-of-bag samples from a file
```bash
python dupdetect --test TRAIN_DIR FILE
``` 
where TRAIN_DIR must point to the bootstrap results from the Mode 2 execution. If not specificed, TRAIN_DIR is 'results'. 

Output is written to standard out, but it is advised to write it to file for later inspection. 
This can be done by appending ` > output.txt` or ` | tee output.txt` to any of the above commands. (This overwrites any existing file named output.txt)

## Input product file
The file should look something like this:

```
{
    "modelID1": [{
        "title": "My product",
        "modelID": "modelID1",
        "featuresMap": {
            ...
        },

        "shop": "someshop.com",
        "url": "https://someshop.com/products/modelID1"
    }],
    "modelID2": [{
        ...
    }],
    ...
}
```
The `featuresMap` key may contain any specification key-value pairs obtained from the webshop.

Note: multiple brands with the same modelID are also put under the same top-level key. 

## Project structure 
The project consists of a single package `dupdetect` which can be invoked, running the __main__.py file inside the dupdetect package.
This file only handles command line input and explanation. Run `python dupdetect -h` to see help information about the command line options. 

### Modules
The `detect.py` is runs the entire duplicate detection algorithm for a certain combination of settings. This is performs all duplicate detection and immediate evaluation. 

The `minhashing.py` module handles converting product representations to signatures and finding the options for band configurations and the corresponding threshold value. 

The `lsh.py` module handles mapping signatures to buckets by band, as well as the additional model-id hashing step (combined with the `,model_ids.py` module, which defines the model-id detection/extraction).

The `compare.py` module handles comparing candidate pairs (in this case using jaccard similarity, but another measure can be swapped in). 

The `optimize.py` module handles the generation of bootstraps and training/testing using bootstraps. 

The `evaluate.py` contains useful functions for determining the performance of the method and is invoked mainly by other modules such as `detect.py` and `optimize.py`.

The `preprocessing.py` module takes care of preprocessing the product representations and obtaining the word set for a product.

The `similarity.py` module contains the definions of similarity measures (only Jaccard for now). 


## Data
The used dataset is the TVs obtained from 4 different webshops (amazon.com, newegg.com, bestbuy.com, thenerds.net) and is publicly available via [https://personal.eur.nl/frasincar/datasets/TVs-all-merged.zip](https://personal.eur.nl/frasincar/datasets/TVs-all-merged.zip)
