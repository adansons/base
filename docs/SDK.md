# Python Reference

- base.config
    - [func check_project_exists](#checkprojectexists)
    - [func delete_project_config](#deleteprojectconfig)
    - [func get_access_key](#getaccesskey)
    - [func get_project_uid](#getprojectuid)
    - [func get_user_id](#getuserid)
    - [func get_user_id_from_db](#getuseridfromdb)
    - [func register_access_key](#registeraccesskey)
    - [func register_project_uid](#registerprojectuid)
    - [func register_user_id](#registeruserid)
    - [func update_project_info](#updateprojectinfo)
- base.dataset
    - [class Dataset](#dataset-class)
- base.file
    - [class File](#file-class)
    - [class Files](#files-class)
- base.hash
    - [func calc_file_hash](#calcfilehash)
- base.parser
    - [class Parser](#parser-class)
- base.project
    - [class Project](#project-class)
    - [func archive_project](#archiveproject)
    - [func create_project](#createproject)
    - [func delete_project](#deleteproject)
    - [func get_projects](#getprojects)

## **check_project_exists()**

```python
function base.config.check_project_exists(user_id="string", project_name="string")
```

Check project is already exists or not

**Parameters**

- user_id (string) - requeired
    - aquired user id from environment variable or config file
- project_name (string) - requeired
    - target project name

**Returns**

- project_exists (bool)
    - project already exists or not

→ [Back to top](#python-reference)

## **delete_project_config()**

```python
function base.config.delete_project_config(user_id="string", project_name="string")
```

Delete config of specified project.

**Parameters**

- user_id (string) - requeired
    - aquired user id from environment variable or config file
- project_name (string) - requeired
    - target project name

→ [Back to top](#python-reference)

## **get_access_key()**

```python
function base.config.get_access_key()
```

Get access key from config file. If you have 'BASE_ACCESS_KEY' on environment variables, Base will use it

**Returns**

- access_key (string)
    - aquired API access key from environment variable or config file

→ [Back to top](#python-reference)

## **get_project_uid()**

```python
function base.config.get_project_uid(user_id="string", project_name="string")
```

Get project uid from project name.

**Parameters**

- user_id (string) - requeired
    - aquired user id from environment variable or config file
- project_name (string) - requeired
    - target project name

**Returns**

- project_uid (listringst)
    - project uid of given project name

→ [Back to top](#python-reference)

## **get_user_id()**

```python
function base.config.get_user_id()
```

Get user id from config file. If you have 'BASE_USER_ID' on environment variables, Base will use it

**Returns**

- user_id (string)
    - aquired user id from environment variable or config file

→ [Back to top](#python-reference)

## **get_user_id_from_db()**

```python
function base.config.get_user_id_from_db(access_key="string")
```

Get user id from remote db.

**Parameters**

- access_key (string) - requeired
    - aquired API access key from environment variable or config file

**Returns**

- user_id (string)
    - aquired user id from database

→ [Back to top](#python-reference)

## **register_access_key()**

```python
function base.config.register_access_key(access_key="string")
```

Register access key to local config file.

**Parameters**

- access_key (string) - requeired
    - API access key

→ [Back to top](#python-reference)

## **register_project_uid()**

```python
function base.config.register_project_uid(user_id="string", project="string", project_uid="string")
```

Register project uid to local config file.

**Parameters**

- user_id (string) - requeired
    - aquired user id from environment variable or config file
- project (string) - requeired
    - target project name
- project_uid (string) - requeired
    - target project uid

→ [Back to top](#python-reference)

## **register_user_id()**

```python
function base.config.register_user_id(user_id="string")
```

Register user id to local config file.

**Parameters**

- user_id (string) - requeired
    - target user id

→ [Back to top](#python-reference)

## **update_project_info()**

```python
function base.config.update_project_info(user_id="string")
```

Update local project info with remote.

**Parameters**

- user_id (string) - requeired
    - aquired user id from environment variable or config file

→ [Back to top](#python-reference)

## **Dataset class**

```python
class base.dataset.Dataset
```

This is a middle-level (numpy or other) interface for dataset in Base. Dataset class receive Files class as an argument and process each data file with specified transform functions. You can create high-level (torch tensor or other) interface for dataset, like Dataloader of Pytorch, using this Dataset object.

```python
import base

project = base.Project("project-name")
files = project.files(conditions="string", query=["string"], sort_key="string")
dataset = base.Dataset(files=files, target_key="string", transform=None|Callable)
```

These are the available attributes:

- transform (Callable)
    - preprocess function
- target_key (string)
    - object variable for modeling
- files (Files)
    - inherited dataset interface
- convert_dict (dict)
    - categorical converter for object variable

These are the available methods:

- [train_test_split()](#traintestsplit)

### **train_test_split()**

```python
x_train, x_test, y_train, y_test = dataset.train_test_split(split_rate=float)
```

This method splits dataset for 2 folds. You can adjust split ratio with `split_rate` option.

**Parameters**

- split_rate (float) - default 0.25
    - the ratio of test set

**Returns**

- x_train (list)
    - transformed train data
- x_test (list)
    - transformed test data
- y_train (list)
    - train label specified as target_key in Dataset class initialization
- y_test (list)
    - test label specified as target_key in Dataset class initialization

→ [Back to top](#python-reference)

## **File class**

```python
class base.files.File
```

Using the index operator [] on the Files class object, you can get the File class object at a specific index.

```python
print(files[0])
>>> "/home/xxxx/dataset/mnist/0/12909.png"
```

These are the available attributes:

- path (string)
    - local filepath.
    
    For example:
    
    ```python
    files[0].path
    >>> "/home/xxxx/dataset/mnist/0/12909.png"
    ```
    
- attrs (dict)
    - attributes (metadata) which related with this file.
    
    For example:
    
    ```python
    files[0].label
    >>> "0"
    
    files[0].id
    >>> "12909"
    ```

→ [Back to top](#python-reference)

## **Files class**

```python
class base.files.Files
```

This is a low-level (file path) interface for dataset in Base. A Files object includes the File instances which matched with your dataset filter.

```python
import base

project = base.Project("project-name")
files = project.files(conditions="string", query=["string"], sort_key="string")
```

You can filter data files and get Files object simply by specified criteria using `files` method of `base.Project`.


**Using the index operator [] on the Files class object, you can get the [`File class`](#file-class) object at a specific index.**

For example:

```python
files[0]
>>> "/home/xxxx/dataset/mnist/0/12909.png"

files[0].label
>>> "0"

files[0].id
>>> "12909"
```

These are the available attributes:

- project_name (string)
    - registerd project name
- user_id (string)
    - registerd user id
- project_uid (string)
    - project unique hash
- conditions (string) - default `None`
    - value to search for files
- query (string) - default []
    - expression of key and value to search for files
- sort_key (string) - default `None` 
    - key to sort files
- files (list)
    - list of File class objects
- result (list)
    - list of metadata_dict filtered by criteria
    ```python
    [
    		{
    				"FilePath": String,
    				"MetaKey1": ...,
    				...
    		},
    		...
    ]
    ```
- paths (list)
    - list of local filepaths
    ```python
    [
    		"String",
    		...
    ]
    ```
- items (list)
    - list of metadata_dict other than filepath
    ```python
    [
    		{
    				"MetaKey1": ...,
    				...
    		},
    		...
    ]
    ```

This is the available methods:

- [filter()](#filter)

### **filter()**

```python
files = files.filter(conditions="string", query=["string"], sort_key="string")
```

This method apply additional filter to already filtered Files object. You can use this method repeatedly.

**Parameters**

- conditions (string) - optional
    - value to search for files.
    
    For example:
    
    ```python
    conditions="0"
    ```
    
    If you want to search by multiple criteria, you must provide comma (,) separated strings. 
    
    For example:
    
    ```python
    conditions="0,1,2"
    ```
    
    You will get  files that meet at least one of the criteria. 
    
    **Note**
    
    There must be no single-byte spaces between values.
    
- query (list) - default []
    - expression of key and value to search for files.
    
    For example:
    
    ```python
    query=["label == 0"]
    ```
    
    You can use `==`, `!=`, `>`, `>=`, `<`, `<=`, `is`, `is not`, `in`, and `not in`  as operators.
    
    If you want to search by multiple criteria, you must provide the list of expressions.  For example:
    
    ```python
    query=["label == 0", "id >= 10000"]
    ```
    
    You will get  files that meet all the criteria.
    
    **Note**
    
    A single-byte space is required before and after the operator.
    
- sort_key (string) - optional
    - key to sort files.
    
    For example:
    
    ```python
    sort_key="label"
    ```

**Returns**

- Files class

There are available operators

 - [＋ (concatenation)](#+-(concatenatopm))
 - [| (union)](#|-(union))

 ### **+ (concatenation)**
Return a new Files object that is the concatenataion of the 2 Files object. You can use this operator recursively.

This operation is **not** sensitive to element duplication. If both Files objects has same File object, the operated Files object has 2 same File object.

**Expression**
```python
concated_files = files1 + files2

# You can operate recursively.
concated_files = files1 + files2 + files3
concated_files2 = concated_files + files4
```

**Examples**
 ```python
files1 = project.files(conditions="20220418", query=["hour >= 018"], sort_key="hour")
files2 = project.files(conditions="20220419", query=["hour >= 021"], sort_key="hour")

files = files1 + files2
print(files)
>>> ======Files======
     Files1(project_name="project-name", conditions="20220418", query=["hour >= 018"], sort_key="hour", file_num=160)
     Files2(project_name="project-name", conditions="20220419", query=["hour >= 021"], sort_key="hour", file_num=100)
     ===Expressions===
     Files1 + Files2

print(len(files))
>>> 260
 ```


 ### **| (union)**
Return a new Files object that is the union of the 2 Files object. You can use this operator recursively.

This operation guaranteed that all File objects that operated Files object has are unique.

**Expression**
```python
union_files = files1 | files2

# You can operate recursively.
union_files = files1 | files2 | files3
union_files2 = union_files | files4
```

**Examples**
 ```python
files1 = project.files(query=["hour >= 020"], sort_key="hour")
files2 = project.files(conditions="20220426,20220429", query=["hour >= 17"], sort_key="hour")

files = files1 + files2
print(files)
>>> ======Files======
     Files1(project_name="project-name", conditions=None, query=["hour >= 020"], sort_key="hour", file_num=650)
     Files2(project_name="project-name", conditions="20220426,20220429", query=["hour >= 017"], sort_key="hour", file_num=200)
     ===Expressions===
     Files1 or Files2

print(len(files))
>>> 710
 ```



→ [Back to top](#python-reference)

## **calc_file_hash()**

```python
function base.hash.calc_file_hash(path="string", algorithm="md5"|"sha224"|"sha256"|"sha384"|"sha512"|"sha1", split_chunk=False|True, chunk_size=int)
```

Calculate hash value of each file

**Parameters**

- path (string) - requeired
    - target file path
- algorithm (string) - default "sha256"
    - hash algorithm name
- split_chunk (bool) - default True
    - if True, split large file to byte chunks
- chunk_size (integer) - default 2048
    - block byte size of chunk

**Returns**

- digest (string)
    - hash string of inputed file

→ [Back to top](#python-reference)

## **Parser class**

```python
class base.parser.Parser
```

This is a file path parser. When you call `add_datafiles` method of `base.Project`, Base will initialize Parser object with specified parsing rule and try to extract metadata from each file path with `__call__` method.

```python
from base.parser import Parser

parser = Parser(parsing_rule="string", sep=None|"string")
result = parser(path="string")
```

### **\_\_init\_\_()**

Initialize self with parsing_rule and generate parser.

```python
base.parser.Parser(parsing_rule="string", sep=None|"string")
```

1. Replace unused strings with `{_}` in `parsing_rule`
2. Extract keys enclosed in `{}`
* Example of processing method
    ```Raw
    1. parsing_rule: hoge{num1}/fuga{num2}.txt
        -> {hoge}/{num1}/{fuga}/{num2}.txt
    
    2. {_}/{num1}/{_}/{num2}.txt
        -> ["_", "num1", "_", "num2"]
    ```

**Parameter**

- parsing_rule (string) - required
    - specified parsing rule  
    ex.) {_}/{name}/{timestamp}/{sensor}-{condition}_{iteration}.csv
- sep (string) - optional
    - the separator of the file path

### **\_\_call\_\_()**

Parse your target path.

```python
parser(path="string")
```

1. Convert file path string to parsable format.
2. Extract values enclosed in `{}` in the parsable formatted path.
3. Generate a dictionary from keys and values extracted with `parsing_rule`.

* Example of processing method
    ```Raw
    1. path: mnist/train/0/12909.png
        -> {mnist}/{train}/{0}/{12909}.png

    2. parsable format: {mnist}/{train}/{0}/{12909}.png
        -> ["mnist", "train", "0", "12909"]

    3. keys  : ["_", "dataType", "label", "id"]
       values: ["mnist", "train", "0", "12909"]
        -> {"dataType": "train", "label": "0", "id": "12909"}
    ```
**Parameters**

- path (string) - required
    - the file path

**Return**

- parsed_dict (dict)
    - meta data dictionary

These are the available methods:

- [is_path_parsable()](#is_path_parsable)
- [update_rule()](#update_rule)

### **is_path_parsable()**

Verify specified parsing rule is working properly. If not, return False

```python
parser.is_path_parsable(path="string")
```

**Parameter**

- path (string) - required
    - the file path.

**Return**

- parsable_flag (bool)
    - True if the file path is parsable

### **update_rule()**

Generate a parser that takes into account the number of splitter based on the parsing example.

Use this method when `is_path_parsable("your-path")` is false.

```python
parser.update_rule(parsing_rule="string")
```

**Parameters**
- parsing_rule (string) - required
    - detail parsing rule.  
    ex.) {Origin}/{train}/{2022_04_05}-{dog}_{a01}.png

→ [Back to top](#python-reference)

## **Project class**

```python
class base.project.Project
```

A basement class of project. You have to initialize with existing project name. If you specified a project name which you don't have, you will get ValueError. Please retry after call `base.project.create_project` function.


```Python
import base

project = base.Project("project-name")
```

These are the available attributes:

- project_name (string)
    - registerd project name
- user_id (string)
    - registerd user id
- project_uid (string)
    - project unique hash

These are the available methods:

- [add_datafile()](#adddatafile)
- [add_datafiles()](#adddatafiles)
- [add_member()](#addmember)
- [add_metafile()](#addmetafile)
- [files()](#files)
- [get_members()](#getmembers)
- [get_metadata_summary()](#getmetadatasummary)
- [link_datafiles()](#linkdatafiles)
- [remove_member()](#removemember)
- [update_member()](#updatemember)


### **add_datafile()**

Import meta data of one file.

```python
project.add_datafile(file_path="string", attributes={"string":"string"})
```

1. Calculate the file hash.
3. Create meta data record with the file hash and attributes.
4. Add that record into project database table.

```python
{
	"FileHash": String,
	"MetaKey1": ...,
	...
}
```

**Parameters**

- file_path (string) - requeired
    - the file path
- attributes (dict) - default {}
    - the extra meta data (attributes)

**Raises**

- Exception
    - raises if something went wrong on uploading request to server

### **add_datafiles()**

Import meta data related with datafile paths.

```python
project.add_datafiles(dir_path="string", extension="string", attributes={"string":"string"}, parsing_rule="string", detail_parsing_rule="string")
```

1. Calculate the file hash.
2. Parse the file path with `parsing-rule`.
3. Create meta data records with the file hash, attributes, and parsed path data.
4. Add that records into project database table.

```python
{
	"FileHash": String,
	"MetaKey1": ...,
	...
}
```

**Parameters**

- dir_path (string) - requeired
    - the root directory path for datafiles
- extension (string) - requeired
    - the extension of datafiles
- attributes (dict) - default {}
    - the extra meta data (attributes) combined with whole datafiles
- parsing_rule (string) - optional
    - the rule for extracting meta data from datafile path
    ex.) {_}/{disease}/{patient-id}-{part}-{iteration}.png
- detail_parsing_rule (string) - optional
    - detail information about parsing rule
    ex.) {_}/{CancerA}/{1-123}-{1}-{100}.png

**Returns**

- file_num (integer)
    - number of imported datafiles

**Raises**

- ValueError
    - raises if invalid parsing rule was specified
- Exception
    - raises if something went wrong on uploading request to server

### **add_member()**

Invite a new project member.

```python
project.add_member(member="string", permission_level="string")
```

**Parameters**

- member (string) - requeired
    - the user id of new member
- permission_level (string) - requeired
    - new member's permission level
        - Viewer
            only read meta data on project database. 
            viewer can not import data files or external files
            and can not control permission of other members.
        - Editor
            can read and write meta data into project database.
            editor can not control permission of other members.
        - Admin
            can read and write meta data into project database.
            admin can also control permission of other members,
            but can not transfer Owner permission level.

**Raises**

- ValueError
    - raises if invalid permission level was specified
- Exception
    - raises if something went wrong on invite request to server

### **add_metafile()**

Import meta data from external file.

```python
project.add_metafile(file_path="string", attributes={"string":"string"})
```

**Parameters**

- file_path (string) - requeired
    - the external file path
- attributes (string) - default {}
    - the extra meta data (attributes) combined with whole datafiles

**Raises**

- ValueError
    - raises if specified external file is not csv or excel file
- Exception
    - raises if something went wrong on uploading request to server

### **files()**

Return the `[Files class](#files-class)`.
You can filter files easily and simply by specified criteria.

```python
files = project.files(conditions="string", query=["string"], sort_key="string")
```

**Parameters**

- conditions (string) - optional
    - value to search for files
    
    For example:
    
    ```python
    conditions="0"
    ```
    
    If you want to search by multiple criteria, you must provide comma (,) separated strings.
    
    For example:
    
    ```python
    conditions="0,1,2"
    ```
    
    You will get  files that meet at least one of the criteria. 
    
- query (list) - default []
    - expression of key and value to search for files
    
    For example:
    
    ```python
    query=["label == 0"]
    ```
    
    You can use `==`, `!=`, `>`, `>=`, `<`, `<=`, `is`, `is not`, `in`, and `not in`  as operator.
    
    If you want to search by multiple criteria, you must provide the list of expressions.
    
    For example:
    
    ```python
    query=["label == 0", "id >= 10000"]
    ```
    
    You will get  files that meet all the criteria.
    
    **Note**
    
    A single-byte space is required before and after the operator.
    
- sort_key (string) - optional
    - key to sort files.
    
    For example:
    
    ```python
    sort_key="label"
    ```

**Returns**

- `[Files class](#files-class)`

### **get_members()**

Get list of project members.

```python
project.get_members()
```

**Returns**

- member_list (list)
    - list of each members information

```JavaScript
[
    {
        "UserID": String,
        "UserRole": String,
        "CreatedTime": String of unix time
    },
    ...
]
```

**Raises**

- Exception
    - raises if something went wrong with request to server

### **get_metadata_summary()**

Get list of meta data information.

```python
project.get_metadata_summary()
```

**Returns**

- key_list (list)
    - list of each members information

```JavaScript
[
    {
        "KeyHash": String,
        "KeyName": String,
        "ValueHash": String,
        "ValueType": String,
        "RecordedCount": Integer,
        "UpperValue": String,
        "LowerValue": String,
        "CreatedTime": String of unix time,
        "LastModifiedTime": String of unix time,
        "Creator": String,
        "LastEditor": String,
        "EditerList": List of String
    },
    ...
]
```

**Raises**

- Exception
    - raises if something went wrong with request to server


### **link_datafiles()**

Create linker metadat to local datafiles.

```python
project.link_datafiles(dir_path="string", extension="string")
```

**Parameters**

- dir_path (string) - requeired
    - the root directory path for datafiles
- extension (string) - requeired
    - the extension of datafiles

**Returns**

- file_num (integer)
    - number of linked datafiles

### **remove_member()**

Remove project member.

```python
project.remove_member(member=["string"]|"string")
```

**Parameters**

- member (list or string) - requeired
    - the target member for removing

**Raises**

- Exception
    - raises if something went wrong on removing request to server

### **update_member()**

Update project member's permission.

```python
project.update_member(member="string", permission_level="Viewer"|"Editor"|"Admin"|"Owner")
```

**Parameters**

- member (string) - requeired
    - the user id of existing member
- permission_level (string) - requeired
    - member's permission level for update
        - Viewer
            only read meta data on project database. 
            viewer can not import data files or external files
            and can not control permission of other members.
        - Editor
            can read and write meta data into project database.
            editor can not control permission of other members.
        - Admin
            can read and write meta data into project database.
            admin can also control permission of other members,
            but can not transfer Owner permission level.
        - Owner
            can transfer owner permission to others,
            and delete project completely.

**Raises**

- ValueError
    - raises if invalid permission level was specified
- Exception
    - raises if something went wrong on invite request to server

→ [Back to top](#python-reference)

## **archive_project()**

```python
function base.project.archive_project(user_id="string", project_name="string")
```

Archive project.

**Parameters**

- user_id (string) - requeired
    - registerd user id
- project_name (string) - requeired
    - project name you want to archive

**Raises**

- Exception
    - raises if something went wrong on request to server


## **create_project()**

```python
function base.project.create_project(user_id="string", project_name="string", private=True|False)
```

**Parameters**

- user_id (string) - requeired
    - registerd user id
- project_name (string) - requeired
    - project name which you want to create
- private (bool) - default True
    - specifies whether or not to allow public access into the project

**Returns**

- project_uid (string)
    - project unique hash

**Raises**

- Exception
    - raises if something went wrong on request to server


## **delete_project()**

```python
function base.project.delete_project(user_id="string", project_name="string")
```

Delete project.

**Parameters**

- user_id (string) - requeired
    - registerd user id
- project_name (string) - requeired
    - archived project name you want to delete

**Raises**

- Exception
    - raises if something went wrong on request to server

## **get_projects()**

```python
function base.project.get_projects(user_id="string", archived=False|True)
```

Get list of projects.

**Parameters**

- user_id (string) - requeired
    - registerd user id
- archived (bool) - default False
    - if False, return not archived projects. if False, return archived projects

**Returns**

- project_list (list)
    - list of project name you have

**Raises**

- Exception
    - raises if something went wrong on request to server

→ [Back to top](#python-reference)
