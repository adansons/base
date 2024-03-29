# Command Reference

Here we provide the specifications, complete descriptions, and comprehensive usage examples for `base` commands. For a list of commands, type `base --help.`

  - [import](#import)
  - [invite](#invite)
  - [link](#link)
  - [list](#list)
  - [new](#new)
  - [rm](#rm)
  - [search](#search)
  - [show](#show)

## import

---

Import data files or external meta data files into Base project.

**Synopsis**

---

```
usage: base import project [-d <datafiles-dirpath>] [-e <datafile-extension>] [-c <path-parsing-rule>] [-m] [-p <external-filepath>] [-a <additional-key-value>]

positional arguments:
  project              your project name to import.
```

**Description**

---

This command provide you the way to import meta data related with data file paths and defined in external files such as `.xlsx`, `.csv`.

You have to select import mode as data files or external files.

If you want to import data files, you have to specify `-d`, `-c` and `-e` options (or prompt ask you interactively).

And then, Base will take below actions.

1. Calculate the file hash.
2. Parse the file path with `parsing-rule`.
3. Create meta data records with the file hash and parsed path data.
4. Add that records into project database table.

```
{
	"FileHash": String,
	"MetaKey1": ...,
	...
}
```

If you want to import external files, you have to specify `-m` and `-p` options.

And then, Base will take below actions.

1. Extract tables from the external file.
2. Parse each table and detect headers in the table.
3. Set header as Key and create meta data records.
4. Link and update existing records with new meta data records in project database table.

```
{
	"Table0,MetaKey1": ...,
	...
}
```

**Options**

---

- `-d <datafiles-dirpath>`, `--directory <datafiles-dirpath>` - specify a `datafiles-dirpath` to load data files which have an extension specified with `-e` option. Base will search recursively.
- `-e <datafile-extension>`, `--extension <datafile-extension>` - specify a `datafile-extension` to filter the targets on load data files. if you have some extensions in one dataset (such as png and jpg), you have to split loading workflow.
- `-c <path-parsing-rule>`, `--parse <path-parsing-rule>` - specify `path-parsing-rule` to extract meta data from each data file path.
    
    ```
    - you can use {key-name} to parse phrases with key.
    - you can use {_} to ignore some phrases.
    - you have to use '/' as separator.
    
    >>> sample parsing rule: {}/{name}/{timestamp}/{sensor}-{condition}{iteration}.csv
    ```
The following options are used only when importing external files.
- `-m`, `--external-file` - parse the content of external files which specified with `-p` option.
- `-p <external-filepath>`, `--path <external-filepath>` - specify an `external-filepath` to import external files. Base will parse content of that file, extract table data on it, and parse the tables.
- `-a <additional-key-value>`, `--additional <additional-key-value>` - specify additional meta data you want to add whole the file you import. the value must be include colon (”:”) between `key name` and `value string`. for instance, if you want to import and join an external file for only “test” data type files, you should specify like `-x dataType:test`.
- `--extract` - with this option, only extract the content of external file, dose not link and update with existing tables. you can specify output path with `-e` and `-o` options to get extract results.
  - `--export <export-file-type>` - if you want to convert extract results into CSV, you can specify CSV as export-file-type.
  - `--output <output-filepath>`- specify output-filepath to save dataset file. default is “./{external-filepath}_Table{number}.csv”
- `--estimate-rule` - with this option, only estimate the joining rule from existing tables and external files which specified with `-p` option, dose not link and update with existing tables.

**Example: Import png files on project “mnist”**

---

```
# after you download mnist data files based on Tutorial1
$ base import mnist --directory ~/dataset/mnist --extension png --parse "{dataType}/{label}/{id}.png"
```

<details><summary>Output</summary>

```
Check datafiles...
found 70000 files with png extension.
70000/70000 files uploaded.   
Success!
```
</details>

**Example: Import external csv file on project “mnist”**

---

```
# download external csv
$ curl -SL https://raw.githubusercontent.com/youkaichao/mnist-wrong-test/master/wrongImagesInMNISTTestset.csv > ~/Downloads/wrongImagesInMNISTTestset.csv

$ base import mnist --external-file --path ~/Downloads/wrongImagesInMNISTTestset.csv -a dataType:test
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
        If you need to modify it, please enter 'm'
                Definition YML file with estimated table join rules will be downloaded, then you can modify it and apply the new join rule.
        Enter a value: y
Success!
```
If you enter 'm', definition YAML file with estimated table join rules will be downloaded.  
You can modify this file and execute the commands displayed in the terminal to apply the new join rule.  

```
Do you want to perform table join?
        Base will join tables with that rule described above.

        'y' will be accepted to approve.

        If you need to modify it, please enter 'm'
                Definition YML file with estimated table join rules will be downloaded, then you can modify it and apply the new join rule.
        Enter a value: m

Downloaded a YAML file 'joinrule_definition_mnist.yml' in current directory.
Key information for the new table and the existing table is as follows.


===== New Table1 =====
KEY NAME         VALUE RANGE  VALUE TYPE            RECORDED COUNT
'index'          8 ~ 9850     int('index')          74            
'originalLabel'  0 ~ 9        int('originalLabel')  74            
'correction'     -1 ~ 8or9    str('correction')     74            
'dataType'       test ~ test  str('dataType')       74            

===== Existing Table =====
KEY NAME    VALUE RANGE   VALUE TYPE       RECORDED COUNT
'id'        0 ~ 59999     str('id')        70000         
'label'     0 ~ 9         str('label')     70000         
'dataType'  test ~ train  str('dataType')  70000          

You can apply the new join-rule according to 2 steps.
1. Modify the file 'joinrule_definition_mnist.yml'. Open the file to see a detailed description.
2. Execute the following command.
   base import mnist --external-file --additional dataType:test --join-rule joinrule_definition_mnist.yml

Success!
```
joinrule_definition_mnist.yml
```yaml
RequestedTime: 1654257223.4988642
ProjectName: mnist
Body:
  Table1:
    FilePath: /Users/user/Downloads/wrongImagesInMNISTTestset.csv
    JoinRules:
      index: id
      originalLabel: label
      correction:
      dataType: dataType
```
New join rules can be defined by modifying the `Body/Table/JoinRules` section.  
Fundamentally, this section consists of Key-Value Pairs. Key is the key name from the new table extracted from the external file. Value is the key name from the existing table.

How to define join rules.  
if you have same key on the new table and the existing table, write like this.
```yaml
 'New table key': 'Existing table key'
```

if you have new value on the existing key, write like this.
```yaml
 'New table key': 'ADD:Existing table key'
```

if you have new key, no need to specify anything.
```yaml
 'New table key': 
```

For example:
```yaml
 JoinRules:
  first_name: name
  age: ADD:Age
  height:
```
1. "first_name: name" means to join the new key named "first_name" with the existing key named "name".
2. "age: ADD:Age" means to add new values of the new key named 'age' on the existing key named 'Age'.
3. "height: " means to add the key named "height" as a new key.



</details>


→ [Back to top](#command-reference)

## invite

Invite collaborators into your Base project.

**Synopsis**

---

```
usage: base invite project [-m <member-id>] [-p <permission-level>] [-u]

positional arguments:
  project              your project name to invite.
```

**Description**

---

This command control access into your project.

You can invite new project member as below `permission level`.

- `Viewer` : only read meta data on project database. viewer can not import data files or external files and can not control permission of other members.
- `Editor` : can read and write meta data into project database. editor can not control permission of other members.
- `Admin` : can read and write meta data into project database. admin can also control permission of other members, but can not transfer `Owner` permission level.

And also you can update member’s permission level with `-u` option, if you are admin or owner.

If you are the project owner and try update other member’s permission to `Owner` , the member will become project owner and your permission will be downgraded to `Admin` .

- `Owner` : can transfer `owner` permission to others, and delete project completely.

**Options**

---

- `-m <member-id>`, `--member <member-id>` - specify `member-id` to invite. if you will be invited by others, you have to tell him/her your user id.
- `-p <permission-level>`, `--permission <permission-level>` -
- `-u`, `--update` -

**Example: Invite an viewer into mnist**

---

check current your project members on mnist with `[base show <project> --member-list](#show)` command

```
$ base show mnist --member-list
```

<details><summary>Output</summary>

```
project Members
===============
xxxx@yyyy.com (Owner, invited at 2022-03-11 18:18:54)
```
</details>

then, invite zzzz@yyyy.com into mnist as an viewer

```
$ base invite mnist --member zzzz@yyyy.com --permission viewer
```

<details><summary>Output</summary>

```
Successfully invited zzzz@yyyy.com into mnist as Viewer
```
</details>

finally, you can check the invited user in project member list .

```
$ base show mnist --member-list
```

<details><summary>Output</summary>

```
project Members
===============
xxxx@yyyy.com (Owner, invited at 2022-03-11 18:18:54)
zzzz@yyyy.com (Viewer, invited at 2022-03-12 13:45:04)
```
</details>

**Example: Update project member’s permission**

---

check current your project members

```
$ base show mnist --member-list
```

<details><summary>Output</summary>

```
project Members
===============
xxxx@yyyy.com (Owner, invited at 2022-03-11 18:18:54)
zzzz@yyyy.com (Viewer, invited at 2022-03-12 13:45:04)
```
</details>

then, update permission of zzzz@yyyy.com to editor

```
$ base invite mnist --update --member zzzz@yyyy.com --permission editor
```

<details><summary>Output</summary>

```
Successfully update zzzz@yyyy.com's permission to Editor
```
</details>

finally, you can check the updated user permission in project member list .

```
$ base show mnist --member-list
```

<details><summary>Output</summary>

```
project Members
===============
xxxx@yyyy.com (Owner, invited at 2022-03-11 18:18:54)
zzzz@yyyy.com (Editor, invited at 2022-03-12 13:45:04)
```
</details>

→ [Back to top](#command-reference)

## link

Link path to data files on local computer and meta data on Base project.

**Synopsis**

---

```
usage: base link project [-d <datafiles-dirpath>] [-e <datafile-extension>]

positional arguments:
  project              your invited project name to link data files.
```

**Description**

---

This command will link data files and meta data records on Base project.

After invitation to project, invited collaborators have to link their data files on local computer.

The data files often locate in different directory with the project owner, and sometimes in different directory name or file name.

So Base will create linker to match local file paths and this enable your collaborators to share the python script which load local file.

**Options**

---

- `-d <datafiles-dirpath>`, `--directory <datafiles-dirpath>` - specify a `datafiles-dirpath` to load data files which have an extension specified with -e option. Base will search recursively.
- `-e <datafile-extension>`, `--extension <datafile-extension>` - specify a `datafile-extension` to filter the targets on load data files. if you have some extensions in one dataset (such as png and jpg), you have to split loading workflow.

**Example: Link mnist data files into invited project**

---

```
$ base link --directory ~/Downloads/mnist --extension png
```

then, you can search and export dataset as you want, or run python modeling script shared by other collaborators.

<details><summary>Output</summary>

```
Check datafiles...
found 70000 files with png extension.
linked!
```
</details>

→ [Back to top](#command-reference)

## list

Show list of Base projects you can access.

**Synopsis**

---

```
usage: base list [--archived]
```

**Description**

---

This command will show you what project you can access.

You can check `Project UID`, your `Role` on the project (”Viewer”, “Editor”, “Admin” or “Owner”), whether the project is `private` or not and project `created date`.

**Options**

---

- `--archived` - show archived projects

**Example: Check projects (not archived)**

---

if you have project “mnist”,

```
$ base list
```

<details><summary>Output</summary>

```
projects
========
[mnist]
Project UID: abcdefghij0123456789
Role: Owner
Private Project: yes
Created Date: 2022-03-11 18:18:54
```
</details>

**Example: Check project (archived)**

---

if you have archived project “fashion-mnist”,

```
$ base list --archived
```

<details><summary>Output</summary>

```
projects
========
[fashion-mnist]
Project UID: klmnopqrst0123456789
Role: Owner
Private Project: yes
Created Date: 2022-03-16 01:38:29
```
</details>

> Note: you can archive your projects with [`base rm <project>`](#rm) command.
> 

→ [Back to top](#command-reference)

## new

Create a new Base project.

**Synopsis**

---

```
usage: base new project

positional arguments:
  project              your project name to create.
```

**Description**

---

This command will create database table for meta data.

1. issue 20 characters as `project unique id (Project UID)` and create tables.
2. save Project UID at `~/.base/projects` file on your local computer.
3. you can use `project name` as alias to Project UID with any Base command.

**Example**

---

```
$ base new mnist
```

<details><summary>Output</summary>

```
Your Project UID
----------------
abcdefghij0123456789

save Project UID in local file (~/.base/projects)
```
</details>

then, project uids will save on `~/.base/projects` .

```
$ cat ~/.base/projects
[xxxx@yyyy.com]
mnist = abcdefghij0123456789
```

> Note: your user id is saved in Global section
> 

→ [Back to top](#command-referenced)

## rm

Archive or completely Delete your Base projects.

**Synopsis**

---

```
usage: base rm project [--confirm] [-m <member-id>]

positional arguments:
  project              your project name to archive or delete.
```

**Description**

---

This command provide you the way to remove project member and archive or delete your project.

If you specify `-m` option, you can remove a project member from the project.

If not, Base will archive or delete specified project.

For prevention unexpected delete, we suppose you to archive project not delete.

If not deleted, you can restore your archived projects.

> Note: Delete project action can be performed only by project owner.
> 

**Options**

---

- `--confirm` - delete archived project completely (only Owner user)
- `-m <member-id>`, `--member <member-id>` - specify a `member-id` to remove from project. you can see your project member list with `[base show <project> --member-list](#show)` command.

**Example: Remove project member**

---

check your project members on mnist with `[base show <project> --member-list](#show)` command

```
$ base show mnist --member-list
```

<details><summary>Output</summary>

```
project Members
===============
xxxx@yyyy.com (Owner, invited at 2022-03-11 18:18:54)
zzzz@yyyy.com (Editor, invited at 2022-03-12 13:45:04)
```
</details>

then, remove zzzz@yyyy.com from mnist

```
$ base rm mnist --member zzzz@yyyy.com
```

<details><summary>Output</summary>

```
zzzz@yyyy.com was removed from mnist
```
</details>

finally, you can check the removed user not in project member list .

```
$ base show mnist --member-list
```

<details><summary>Output</summary>

```
project Members
===============
xxxx@yyyy.com (Owner, invited at 2022-03-11 18:18:54)
```
</details>

**Example: Archive mnist project**

---

```
$ base rm mnist
```

<details><summary>Output</summary>

```
mnist was Archived
```
</details>

then, you can check whether the project was archived with `[base list](#list)` command.

**Example: Delete mnist project**

---

```
$ base rm mnist --confirm
```

<details><summary>Output</summary>

```
mnist was Deleted
```
</details>

then, you can check whether the project was deleted with `[base list](#list)` command.

```
$ base list --archived
```

<details><summary>Output</summary>

```
projects
========
```
</details>

> Note: if you delete the project once, you can not restore its saved data forever.


→ [Back to top](#command-reference)

## search

Search data files and export it based on meta data of Base project.

**Synopsis**

---

```
usage: base search project [-q <query-condition>] [-c <value-conditions>] 
[-e <export-file-type>] [-o <output-filepath>] [-s]

positional arguments:
  project              your project name to search.
```

**Description**

---

This command provide you search engine for data files.

You can search some words in meta data with `-c` option, or set filter with `-q` option.

And also you can export as JSON or CSV with `-e` and `-o` options.

> Note: if you have same values on different keys, condition filter will be confused and return a result you have not expected. for secure filtering, you should specify key name with query option if some values duplicated in over 2 keys.

**Options**

---

- `-q <query-condition>`, `--query <query-condition>` - specify `query-condition` to filter the data files based on meta data. you can use various operators and specify multiple `query-condition`.
    
    ```
    [query grammar]
    {KeyName} {Operator} {Values}
    - add 1 spaces each section
    - don't use space any other
    >>> sample query condition: CategoryName == airplane
    
    [operators]
    - == : equal
    - != : not equal
    - >= : greater than
    - <= : less than
    - > : greater
    - < : less
    - is : missing value (only 'None' is allowed as Values, ex. query='correction is None')
    - is not : any value (only 'None' is allowed as Values, ex. query='correction is not None')
    - in : inner list of Values
    - not in : outer list of values
    ```
    
    > Note:  you have to follow query grammar.
    > 
- `-c <value-conditions>`, `--conditions <value-conditions>` - specify `value-conditions` to filter by meta data value. this is so powerful mode because you do not have to know the KeyName of meta data.
    - if you specify multiple value of one meta data key, Base will return you the union of the values.
        - ex.) if you specify "airplane,automobile” and both of them in same meta data key ”CategoryName”, Base will Interpret as “CategoryName is airplane or automobile”.
    - if you specify multiple value of different meta data keys, Base will return you the intersection of the values.
        - ex.) if you specify "airplane,2007” and one of them in meta data key ”CategoryName”, and other in “Timestamp”, Base will Interpret as “CategoryName is airplane and also Timestamp is 2007”.
    - and you can combine these behaviors.
        - ex.) if you specify "airplane,automobile,2007” and two of them in same meta data key ”CategoryName”, and one in “Timestamp”, Base will Interpret as “(CategoryName is airplane and also Timestamp is 2007) or (CategoryName is automobile and also Timestamp is 2007)”.
    
    ```
    [conditions grammar]
    "{Value1},{Value2},..."
    - separate with comma
    >>> sample conditions: "airplane,automobile"
    ```
    
    > Note:  you have to follow conditions grammar.
    > 
- `-e <export-file-type>`, `--export <export-file-type>` - if you want to convert search results into JSON or CSV, you can specify JSON or CSV as `export-file-type`.
- `-o <output-filepath>`, `--output <output-filepath>` - specify `output-filepath` to save dataset file. default is “./dataset.json” or “./dataset.csv”
- `-s`, `--summary` - summarize result and hide detail output

**Example: Search mnist with value conditions**

---

```
$ base search mnist --conditions "train" --query "label in ['1','2','3']"
```

<details><summary>Output</summary>

```
18831 files
========
'/home/xxxx/dataset/mnist/train/1/42485.png'
...
```
</details>

**Example: Search mnist and export as JSON**

---

```
$ base search mnist --conditions "test" --query "correction != -1" --export JSON --output ./dataset.json
```

<details><summary>Output</summary>

```
9963 files
========
'/home/xxxx/dataset/mnist/test/7/3329.png'
...
```
</details>

```
$ cat ./dataset.json
{
	"Data": [
		{
			"FilePath": "/home/xxxx/dataset/mnist/test/7/3329.png",
			"label": "7",
			"dataType": "test",
			"id": "3329"
		},
		...
	]
}
```

→ [Back to top](Command%20Re%2020fe9.md)

## show

Show detail information about your Base project.

**Synopsis**

---

```
usage: base show project [--member-list]

positional arguments:
  project              your project name to show detail.
```

**Description**

---

This command will show you what meta data in your project.

Each meta data has `KeyName (like “CategoryName”)` and `KeyHash` for specify the meta data if you changed KeyName.

The structure of returns likes below.

```
{
	"KeyHash": String,
	"KeyName": String,
	"RecordedCount", Number,
	"Creator": String,
	"LastEditor": String,
	"EditerList": List,
	"ValueHash": String,
	"ValueType": String,
	"UpperValue": String,
	"LowerValue": String,
	"UniqueValues": String,
	"CreatedTime": String of unix time,
	"LastModifiedTime": String of unix time
}
```

Options

---

- `--member-list` - show project members

**Example: Show mnist project**

---

```
$ base show mnist
```

<details><summary>Output</summary>

```
project mnist
===============
You have 70000 records with 4 keys in this project.

[Keys Information]

KEY NAME                 VALUE RANGE   VALUE TYPE                          RECORDED COUNT
'id','index'             0 ~ 59999     str('id'), int('index')             70000         
'correction'             0or6 ~ -1     str('correction')                   74            
'label','originalLabel'  0 ~ 9         str('label'), int('originalLabel')  70000         
'dataType'               test ~ train  str('dataType')                     70000
...
```
</details>

**Example: Show mnist project members**

---

```
$ base show mnist --member-list
```

<details><summary>Output</summary>

```
project Members
===============
xxxx@yyyy.com (Owner, invited at 2022-03-11 18:18:54)
zzzz@yyyy.com (Editor, invited at 2022-03-12 13:45:04)
```
</details>

→ [Back to top](#command-reference)