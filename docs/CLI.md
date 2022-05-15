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
    - you can use {{key-name}} to parse phrases with key.
    - you can use {{_}} to ignore some phrases.
    - you have to use '/' as separator.
    
    >>> sample parsing rule: {{}}/{{name}}/{{timestamp}}/{{sensor}}-{{condition}}{{iteration}}.csv
    ```
    
- `-m`, `--external-file` - parse the content of external files which specified with `-p` option.
- `-p <external-filepath>`, `--path <external-filepath>` - specify an `external-filepath` to import external files. Base will parse content of that file, extract table data on it, and parse the tables.
- `-a <additional-key-value>`, `--additional <additional-key-value>` - specify additional meta data you want to add whole the file you import. the value must be include colon (”:”) between `key name` and `value string`. for instance, if you want to import and join an external file for only “test” data type files, you should specify like `-x dataType:test`.

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

        Enter a value: y
Success!
```
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
    - ¥add 1 spaces each section
    - don't use space any other
    >>> sample query condition: CategoryName == airplane
    
    [operators]
    - == : equel
    - != : not equel
    - >= : greater than
    - <= : less than
    - > : greater
    - < : less
    - in : inner list of Values
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
projects mnist
===============
{'KeyHash': '596d40a4ed24c02a31b19d6e633f46f64304a672b40f793d8c6deab868beb0e2', 'KeyName': 'condition', 'RecordedCount': 1699, ...}
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