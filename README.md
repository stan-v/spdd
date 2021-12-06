# Scalable Product Duplicate Detection
### Author: Stan Verstappen

![spdd_logo](https://user-images.githubusercontent.com/33269018/144854214-7832b6ac-e273-4751-b497-23c3bcd981b3.png)

This repository is an implementation of the Locality Sensitive Hashing algorithm for application in product duplicate detection.

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
The optional argument `--sim SIM` can change the desired similarity for the analysis, for example 
`python dupdetect --sim 0.999 data/data.json`, which will pick the bands to match the desired similarity as close as possible, and uses
this similarity as threshold value.

Mode 2: train on bootstraps from a file:
```bash
python dupdetect --train FILE
``` 
Mode 3: test on out-of-bag samples from a file
```bash
python dupdetect -test TRAIN_DIR FILE
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

