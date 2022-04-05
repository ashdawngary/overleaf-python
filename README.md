# overleaf-python
Python API for automating overleaf operations.

### Constructor

Start by locating your _session_ id, a cookie labeled as `overleaf_session2` after logging into overleaf.  This will be used as proxy for logging in.

Next find the project that you want to connect your client to.  This can be found by the url
`https://www.overleaf.com/project/{project id}`
Finally it suffices to string the two together:
```python
from ofclient import OverleafClient

sess_id = ...
proj_id = ...

client = OverleafClient(sess_id,proj_id)
```

### Features

#### Access the project directory structure

On connect, the client will load the project directory, so you can see what is inside programatically
```python
client.dirData 
```
example output below:
```python
{'_id': '...',
 'docs': [{'_id': '...', 'name': 'main.tex'},
          {'_id': '...', 'name': 'v2.tex'},
          {'_id': '...', 'name': 'vf.tex'},
          {'_id': '...', 'name': 'example_data.txt'},
          {'_id': '...', 'name': 'some_array_data.txt'}],
 'fileRefs': [{'_id': '...',
               'created': '2022-04-03T18:23:02.158Z',
               'linkedFileData': None,
               'name': 'pdf1.pdf'},
              {'_id': '...',
               'created': '2022-04-03T18:23:02.414Z',
               'linkedFileData': None,
               'name': 'pdf2.pdf'},
              {'_id': '...',
               'created': '2022-04-03T18:23:02.581Z',
               'linkedFileData': None,
               'name': 'pdf3.pdf'},
              {'_id': '...',
               'created': '2022-04-03T18:23:02.739Z',
               'linkedFileData': None,
               'name': 'pdf4.pdf'}],
 'folders': [{'_id': '...',
              'docs': [{'_id': '...',
                        'name': 'silent_file.tex'}],
              'fileRefs': [],
              'folders': [{'_id': '...',
                           'docs': [{'_id': '...',
                                     'name': 'example_data.txt'}],
                           'fileRefs': [{'_id': '...',
                                         'created': '2022-04-03T14:51:52.810Z',
                                         'linkedFileData': None,
                                         'name': 'case_6.png'},
                                        {'_id': '...',
                                         'created': '2022-04-03T18:25:27.079Z',
                                         'linkedFileData': None,
                                         'name': 'out.png'},
                                        {'_id': '...',
                                         'created': '2022-04-03T19:35:45.696Z',
                                         'linkedFileData': None,
                                         'name': 'case_13#.png'}],
                           'folders': [],
                           'name': 'subassetsfolder'}],
              'name': 'assets_folder'}],
 'name': 'rootFolder'}

```
This is a dictionary of raw data provided by the server.  Treat it as read only and call `client.resync()` if you need to reload it.


#### Get a file id
Obtains the file id associated with a path (`_id` attr above).  Utility function to traversing the directory easier.
```python
path = ...
client.getFileId(path)
```

#### Get a folder id
Obtains the folder id associated with a path.  Utility function for traversing the folders
```python
path = ...
client.getFolderId(path)
```


