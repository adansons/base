# Adansons Base Document

  - [Product Concept](#product-concept)
  - [0. Get Access Key](#0-get-access-key)
  - [1. Installation](#1-installation)
  - [2. Configuration](#2-configuration)
    - [2.1 with CLI](#21-with-cli)
    - [2.2 Environment Variables](#22-environment-variables)
  - [3. Tutorial 1: Organize meta data and Create dataset](#3-tutorial-1-organize-meta-data-and-create-dataset)
    - [Step 0. prepare sample dataset](#step-0-prepare-sample-dataset)
    - [Step 1. create new project](#step-1-create-new-project)
    - [Step 2. import data files](#step-2-import-data-files)
    - [Step 3. import external metadata files](#step-3-import-external-metadata-files)
    - [Step 4. filter and export dataset with CLI](#step-4-filter-and-export-dataset-with-cli)
    - [Step 5. filter and export dataset with Python SDK](#step-5-filter-and-export-dataset-with-python-sdk)
  - [4. API Reference](#4-api-reference)
    - [4.1 Command Reference](#41-command-reference)
    - [4.2 Python Reference](#42-python-reference)


## Product Concept
- Adansons Base is a data management tool that organizes metadata of unstructured data and creates and organizes datasets.
- It makes dataset creation more effective, helps find essential insights from training results, and improves AI performance.

More detail
↓↓↓

- Medium
  - https://medium.com/@KenichiHiguchi/3-things-you-need-to-deal-with-in-data-management-to-create-best-dataset-781177507fc2
- Product Page
  - https://adansons.wraptas.site

---
## 0. Get Access Key

Type your email into the form below to join our slack and get the access key.

Invitation Form: https://share.hsforms.com/1KG8Hp2kwSjC6fjVwwlklZA8moen


## 1. Installation

Adansons Base contains Command Line Interface (CLI) and Python SDK, and you can install both with `pip` command.

```bash
pip install git+https://github.com/adansons/base
```

> Note: if you want to use CLI in any directory, you have to install with the python globally installed on your computer.

## 2. Configuration

### 2.1 with CLI

when you run any Base CLI command for the first time, Base will ask for your access key provided on our slack.

then, Base will verify the specified access key was correct.

if you don't have an access key, please see [0. Get Access Key](#0-get-access-key).

this command will show you what projects you have

```bash
base list
```

<details><summary>Output</summary>

```
Welcome to Adansons Base!!

Let's start with your access key provided on our slack.

Please register your access_key: xxxxxxxxxx

Successfully configured as xxxx@yyyy.com

projects
========
```
</details>

### 2.2 Environment Variables

if you don’t want to configure interactively, you can use environment variables for configuration.

`BASE_USER_ID` is used for the identification of users, this is the email address you submitted via our form.

```bash
export BASE_ACCESS_KEY=xxxxxxxxxx
export BASE_USER_ID=xxxx@yyyy.com
```

## 3. Tutorial 1: Organize metadata and Create a dataset

let’s start the Base tutorial with the mnist dataset.

### Step 0. prepare sample dataset

install dependencies for download dataset at first.

```bash
pip install pypng
```

then, download a script for mnist from our Base repository

```bash
curl -sSL https://raw.githubusercontent.com/adansons/base/main/download_mnist.py > download_mnist.py
```

run the download-mnist script. you can specify any folder for downloading as the last argument(default “~/dataset/mnist”). if you run this command on Windows, please replace it with the windows path like “C:\dataset\mnist”

```bash
python3 ./download_mnist.py ~/dataset/mnist
```

> Note: Base can link the data files if you put them anywhere on the local computer. So if you already downloaded the mnist dataset, you can use it

after downloading, you can see data files in ~/dataset/mnist.

```
~
└── dataset
     └── mnist
          ├── train
          │ 	 ├── 0
          │ 	 │   ├── 1.png
          │ 	 │   ├── ...
          │ 	 │   └── 59987.png
          │ 	 ├── ...
          │ 	 └── 9
          └──	test
                ├── 0
                └── ...
```

### Step 1. create a new project

create mnist project with [base new <project>](/docs/CLI.md#new) command.

```bash
base new mnist
```

<details><summary>Output</summary>

```
Your Project UID
----------------
abcdefghij0123456789

save Project UID in the local file (~/.base/projects)
```
</details>

Base will issue a Project Unique ID and automatically save it in a local file.

### Step 2. import data files

after step 0, you have many png image files on the”~/dataset/mnist” directory.

let’s upload metadata related to their paths into the mnist project with the `base import` command.

```bash
base import mnist --directory ~/dataset/mnist --extension png --parse "{dataType}/{label}/{id}.png"
```

> Note: if you changed the download folder, please replace “~/dataset/mnist” in the above command.

<details><summary>Output</summary>

```
Check datafiles...
found 70000 files with png extension.
Success!
```
</details>

### Step 3. import external metadata files

if you have external metadata files, you can integrate them into the existing project database with the `—-external-file` option.

in this time, we use `wrongImagesInMNISTTestset.csv` published on Github by youkaichao.

[https://github.com/youkaichao/mnist-wrong-test](https://github.com/youkaichao/mnist-wrong-test)

this is the extra metadata that correct wrong label on the mnist test dataset.

you can evaluate your model more strictly and correctly by using these extra metadata with Base.

download external CSV

```bash
curl -SL https://raw.githubusercontent.com/youkaichao/mnist-wrong-test/master/wrongImagesInMNISTTestset.csv > ~/Downloads/wrongImagesInMNISTTestset.csv
```

```bash
base import mnist --external-file --path ~/Downloads/wrongImagesInMNISTTestset.csv -a dataType:test
```

<details><summary>Output</summary>

```
1 tables found!
now estimating the rule for table joining...

1 table joining rule was estimated!
Below table joining rule will be applied...

Rule no.1

        key 'index'     ->      connected to 'id' key on exist table
        key 'originalLabel'     ->      connected to 'label' key on exist table
        key 'correction'        ->      newly added

1 tables will be applied
Table 1 sample record:
        {'index': 8, 'originalLabel': 5, 'correction': '-1'}

Do you want to perform table join?
        Base will join tables with that rule described above.

        'y' will be accepted to approve.

        Enter a value: y
Success!
```
</details>

### Step 4. filter and export dataset with CLI

now, we are ready to create a dataset.

let’s pick up a part of data files, the label is 0, 1, or 2 for training, from project mnist with `base search <project>` command.

you can use `--conditions <value-only-search>` option for magical search filter and `--query <key-value-pair-search>` option for advanced filter.

Note that the `--query` option can only use the value for searching.



Be careful that you may get so large output on your console without the `-s, --summary` option.

The `--query` option's grammar is below.

`--query {KeyName} {Operator} {Values}`

- add 1 space between each section
- **don't use space any other**

You can use these operators below in the query option.

[operators]
```
  == : equal
  != : not equal
  >= : greater than
  <= : less than
  >  : greater
  <  : less
  in : inner list of Values
  not in : not inner list of Values
```

(check [search docs](/docs/CLI.md#search) for more information).

```bash
base search mnist --conditions "train" --query "label in ['1','2','3']"
```

> Note: in the query option, you have to specify each component as a string in the list without space like `“[’1’,’2’,’3’]”`, when you want to operate `in` or `not in` query.
> 

<details><summary>Output</summary>

```
18831 files
========
'/home/xxxx/dataset/mnist/train/1/42485.png'
...
```
</details>

> Note: If you specify no conditions or query, Base will return whole data files.

If you want to use the 'OR search' with the `--query` command, please use our Python SDK.

### Step 5. filter and export dataset with Python SDK

in python script, you can filter and export datasets easily and simply with `Project class` and `Files class`. (see [SDK docs](/docs/SDK.md#project-class))

(If you don't have the packages below, please install them by using `pip`)
```bash
pip install NumPy pillow torch torchvision
```

```python
from base import Project, Dataset
import numpy as np
from PIL import Image


# export dataset as you want to use
project = Project("mnist")
files = project.files(conditions="train", query=["label in ['1','2','3']"])

print(files[0])
# this returns path-like `File` object
# -> '/home/xxxx/dataset/mnist/0/12909.png'
print(files[0].label)
# this returns the value of attribute 'lable' of first `File` object
# -> '0'

# function to load image from path
# this is necessary, if you want to use image in your dataset
# because base Dataset class doesn't convert path to image
def preprocess_func(path):
    image = Image.open(path)
    image = image.resize((28, 28))
    image = np.array(image)
    return image

dataset = Dataset(files, target_key="label", transform=preprocess_func)

# you can also use dataset objects like this.
for data, label in dataset:
    # data: an image-data. ndarray
    # label: the label of an image data, like 0
    pass

x_train, x_test, y_train, y_test = dataset.train_test_split(split_rate=0.2)

# or use with torch
import torch
import torchvision.transforms as transforms
from PIL import Image

def preprocess_func(path):
    image = transforms.ToTensor()(transforms.Resize((28, 28))(Image.open(path)))
    return image

dataset = Dataset(files, target_key="label", transform=preprocess_func)
loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
```

finally, let’s try one of the most characteristic use cases on Adansons Base.

in the external file, you imported in step.3, some mnist test data files are annotated as `“-1”` in the correction column. this means that it is difficult to classify that files even for a human.

so, you should exclude that files from your dataset to evaluate your AI models more properly.

```python
# you can exclude files which have "-1" on "correction" with below code
eval_files = project.files(conditions="test", query=["correction != -1"])

print(len(eval_files))
# this returns the number of files matched with requested conditions or query
# -> 9963

eval_dataset = Dataset(eval_files, target_key="label", transform=preprocess_func)
```

## 4. API Reference

### 4.1 Command Reference

[Command Reference](/docs/CLI.md)

### 4.2 Python Reference

[Python Reference](/docs/SDK.md)
