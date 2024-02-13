3- Reading
----------

We have already stored information about 3 runs so far. 
We can access this information easily using MLXP's reader module, which allows querying results, grouping, and aggregating them. Let's do this interactively!


Creating a result database
^^^^^^^^^^^^^^^^^^^^^^^^^^

We first start by creating a :samp:`reader` objects that interacts with the logs of multiple runs contained in the same parent directory (here :samp:`./logs/`): 

.. code-block:: ipython

    In [1]: import mlxp

    In [2]: # Creates a database of results stored by the logger that is accessible using a reader object.
       ...: parent_log_dir = './logs/'
            reader = mlxp.Reader(parent_log_dir)


Under the woods, the reader object creates a JSON file :samp:`database.json` in the directory :samp:`parent_log_dir` and stores metadata about all runs contained in that directory. 

.. code-block:: text
   :caption: ./logs/

   logs/
   ├── 1/...
   ├── 2/...
   ├── 3/...
   └── database.json


This database allows, for instance, obtaining general information about the runs contained in the log directory :samp:`parent_log_dir`, such as the number of runs or the list of fields that are stored in the various files of the log directories: (e.g. in :samp:`config.yaml` , :samp:`info.yaml` or :samp:`metrics/`): 


.. code-block:: ipython

   In [3]: # Displaying the number of runs accessible to the reader
      ...: len(reader)
   Out[3]: 3

   In [4]: # Displaying all fields accessible in the database.
      ...: print(reader.fields)
   Out[4]:
                                    Type
   Fields
   config.data.d_int         '<class 'int'>'
   config.data.device        '<class 'str'>'
   config.model.num_units    '<class 'int'>'
   config.num_epoch          '<class 'int'>'
   config.optimizer.lr     '<class 'float'>'
   config.seed               '<class 'int'>'
   info.app                  '<class 'str'>'
   info.cmd                  '<class 'str'>'
   info.end_date             '<class 'str'>'
   info.end_time             '<class 'str'>'
   info.exec                 '<class 'str'>'
   info.hostname             '<class 'str'>'
   info.log_dir              '<class 'str'>'
   info.log_id               '<class 'int'>'
   info.process_id           '<class 'int'>'
   info.start_date           '<class 'str'>'
   info.start_time           '<class 'str'>'
   info.status               '<class 'str'>'
   info.user                 '<class 'str'>'
   info.work_dir             '<class 'str'>'
   train.epoch                    'LAZYDATA'
   train.loss                     'LAZYDATA'


For instance, the method :samp:`fields` displace a table of existing fields along with their type. 
You can see that all the user config options are preceded by the prefix :samp:`config`. 
The table also contains all fields stored in the files :samp:`info.yaml` of the metadata directory for each run. 
Finally, all keys stored by the logger when calling the method :samp:`log_metrics` are also available. 
Note that these keys are of type :samp:`LAZYDATA`, meaning that the database does not store these data but only a reference to them (more on this later). 


Querying the database
^^^^^^^^^^^^^^^^^^^^^
Once the database is created, the reader object allows filtering the database by the values taken by some of its fields. 
Not all fields can make a valid query. Only those obtained when displaying the attribute 'searchable' are acceptable:

.. code-block:: ipython

    In [5]: # Displaying searchable fields must start with info or config
       ...: print(reader.searchable)
    Out[5]:
                                       Type
    Fields
    config.data.d_int         '<class 'int'>'
    config.data.device        '<class 'str'>'
    config.model.num_units    '<class 'int'>'
    config.num_epoch          '<class 'int'>'
    config.optimizer.lr     '<class 'float'>'
    config.seed               '<class 'int'>'
    info.executable           '<class 'str'>'
    info.cmd                  '<class 'str'>'
    info.end_date             '<class 'str'>'
    info.end_time             '<class 'str'>'    info.current_file_path    '<class 'str'>'
    info.hostname             '<class 'str'>'
    info.log_dir              '<class 'str'>'
    info.log_id               '<class 'int'>'
    info.process_id           '<class 'int'>'
    info.start_date           '<class 'str'>'
    info.start_time           '<class 'str'>'
    info.status               '<class 'str'>'
    info.user                 '<class 'str'>'
    info.work_dir             '<class 'str'>'


The :samp:`searchable` fields must start with the prefixes: :samp:`info.` or :samp:`config.` to indicate that they correspond to keys in the files :samp:`config.yaml` and :samp:`info.yaml` of the directories :samp:`metadata` of the logs.  Let's make a simple query and use the :samp:`filter` method: 


.. code-block:: ipython
    
    In [6]: # Searching using a query string
       ... query = "info.status == 'COMPLETE' & config.optimizer.lr <= 0.1"
       ... results = reader.filter(query_string=query, result_format="pandas")

    In [7]: # Display the result as a pandas dataframe 
       ...: results 
    Out[7]:
       config.data.d_int  ...                                         train.loss
    0                 10  ...  [0.030253788456320763, 0.03025251068174839, 0....
    1                 10  ...  [0.030253788456320763, 0.03024102933704853, 0....


Here, we call the method :samp:`filter` with the option :samp:`result_format` set to :samp:`pandas`. This allows to return the result as a pandas dataframe where the rows correspond to runs stored in the :samp:`parent_log_dir` and matching the query. If the query is an empty string, then all entries of the database are returned.  


The dataframe's column names correspond to the fields contained in  :samp:`reader.fields`. These names are constructed as follows:

- The dot-separated flattened keys of the hierarchical options contained in the YAML file :samp:`metadata.yaml` preceded by the prefix :samp:`metadata`.  
- The keys of the dictionaries stored in the files contained in the :samp:`metrics`  directories (here :samp:`train.json`) preceded by the file name as a suffix (here: :samp:`train.`). 

As you can see, the dataframe loads the content of all keys in the files :samp:`train.json` (contained in the :samp:`metrics` directories of each run), which might not be desirable if these files are large. 
This can be avoided using **lazy evaluation** which we describe next.

Lazy evaluation
^^^^^^^^^^^^^^^

Instead of returning the result of the search as a pandas dataframe, which loads all the content of the, possibly large, :samp:`train.json` file, we can return a :samp:`mlxp.DataDictList` object. 
This object can also be rendered as a dataframe but does not load the :samp:`train.json` files in memory unless the corresponding fields are explicitly accessed. 



.. code-block:: ipython

    In [8]: # Returning a DataDictList as a result
       ... results = reader.filter(query_string=query)

    In [9]: # Display the result as a pandas dataframe 
       ...: results 
    Out[9]:
       config.data.d_int config.data.device  ...  train.epoch train.loss
    0                 10                cpu  ...     LAZYDATA    LAZYDATA
    1                 10                cpu  ...     LAZYDATA    LAZYDATA

    [2 rows x 39 columns]

As you can see, the content of the columns :samp:`train.epoch` and :samp:`train.loss` is simply marked as :samp:`LAZYDATA`, meaning that it is not loaded for now. If we try to access a specific column (e.g. :samp:`train.loss`), :samp:`DataDictList` will automatically load the desired result:


.. code-block:: ipython

    In [10]: # Access a particular column of the results 
       ...: results[0]['train.loss'] 
    Out[10]:
    [0.030253788456320763, 0.03025251068174839, 0.030249962583184242, 0.030246131122112274, 0.03024103306233883, 0.030234655365347862, 0.03022700361907482, 0.030218079686164856, 0.030207885429263115, 0.030196424573659897]

The object results should be viewed as a list of dictionaries. Each element of the list corresponds to a particular run in the :samp:`parent_log_dir` directory. The keys of each dictionary in the list are the columns of the dataframe. Finally, it is always to convert a :samp:`DataDictList` object to a pandas dataframe using the method :samp:`toPandasDF`. 


Grouping and aggregation
^^^^^^^^^^^^^^^^^^^^^^^^

While it is possible to directly convert the results of a query to a pandas dataframe which supports grouping and aggregation operations, 
MLXP also provides basic support for these operations. Let's see how this works:


.. code-block:: ipython


    In [11]: # List of group keys.
       ... group_keys = ['config.optimizer.lr']

    In [12]: # Grouping the results 
       ...: grouped_results = results.groupBy(group_keys)
       ...: print(grouped_results)
    Out[12]:
                                 config.data.d_int config.data.device  ...  train.epoch  train.loss
    config.optimizer.lr                                        ...
    0.01                                10                cpu  ...     LAZYDATA    LAZYDATA
    0.10                                10                cpu  ...     LAZYDATA    LAZYDATA

    [2 rows x 38 columns]

The output is an object of type :samp:`GroupedDataDicts`. It can be viewed as a dictionary whose keys are given by the different values taken by the group variables. Here the group variable is the learning rate :samp:`config.optimizer.lr` which takes the values  :samp:`0.01` and :samp:`0.10`. Hence, the keys of :samp:`GroupedDataDicts` are :samp:`0.01` and :samp:`0.10`. Each group (for instance the group with key :samp:`0.01`) is a :samp:`DataDictList` object containing the different runs belonging to that group.

Finally, we can aggregate these groups according to some aggregation operations:


.. code-block:: ipython


    In [13]: # Creating the aggregation maps 
        ... from mlxp.data_structures.contrib.aggregation_maps import AvgStd
        ... agg_maps = [AvgStd('train.loss'),AvgStd('train.epoch')]


    In [14]: # Aggregating the results 
       ...: agg_results = grouped_results.aggregate(agg_maps)
       ...: print(agg_results)
    Out[14]:
                                          train.loss_avg  ... config.optimizer.lr
    0  [0.030253788456320763, 0.03024102933704853, 0....  ...                 0.1
    1  [0.030253788456320763, 0.03025251068174839, 0....  ...                0.01

    [2 rows x 3 columns]

Here, we compute the average and standard deviation of the field :samp:`train.loss` which contains a list of loss values. The loss values are averaged per group and the result is returned as a :samp:`DataDictList` object whose columns consist of:

- The resulting fields: :samp:`train.loss_avg` and :samp:`train.loss_std`
- The original group key: :samp:`config.optimizer.lr`.

Of course, one can always convert these structures to a pandas dataframe at any time!