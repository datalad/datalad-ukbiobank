.. _chap_examples:

Quick Start
***********

Download Data
-------------
To download UK Biobank data for a subject, start by creating and initializing a
new dataset. In this example, two data records with two *instances* (sessions)
each are selected.

.. code::

  datalad create sub-1002532
  cd sub-1002532
  datalad ukb-init 1002532 20227_2_0 20227_3_0 20249_2_0 20249_3_0

After initialization, run ``ukb-update`` to download data from the UK Biobank.

.. code::

  datalad ukb-update --keyfile <path_to_keyfile> --merge

This will create two branches:

* ``incoming``: the pristine archives downloaded from UK Biobank
* ``incoming-native``: the extracted files in the original layout provided by
  the UK Biobank

With ``ukb-update --merge``, content is merged from ``incoming-native``
into the active branch automatically.

Get Updates
-----------
To update a single subject's dataset, simply re-run ``ukb-update`` to
re-download the data and register any potential changes. Running ``ukb-update``
will always re-download the data, regardless if there are upstream changes.
Again, the ``--merge`` option will merge any updates into the active branch.

.. code::

  datalad ukb-update --keyfile <path_to_keyfile> --merge

Add or Remove Data Types
------------------------
To add/remove data types, first re-initialize the dataset (with ``--force``) to
select the new data types. In this example, another data record with two
*instances* (sessions) is added to the list of selected data records.

.. code::

  datalad ukb-init --force 1002532 20227_2_0 20227_3_0 20249_2_0 20249_3_0 20250_2_0 20250_3_0

After re-initialization, run ``ukb-update`` to download the data.

.. code::

  datalad ukb-update --keyfile <path_to_keyfile> --merge

Structure in BIDS
-----------------
To enable a BIDS(-like) layout of the data, re-initialize the dataset with the
``--bids`` option. This option can also be used when first initializing the
dataset.

.. code::

  datalad ukb-init --force --bids 1002532 20227_2_0 20227_3_0 20249_2_0 20249_3_0 20250_2_0 20250_3_0

After re-initialization, run ``ukb-update`` to create an additional
``incoming-bids`` branch containing a BIDS(-like) conversion of the extracted
downloads. If the ``--merge`` option is specified, it will merge the
``incoming-bids`` branch into the active branch.

.. code::

  datalad ukb-update --keyfile <path_to_keyfile> --merge --force

The BIDS conversion only happens if the re-downloaded data is different from
the previously download data. If there are no changes to the content on
re-download, but you want to initiate the BIDS conversion, the ``--force``
option can be used.

Save Space
----------
The ``--drop`` option can be used to avoid storing multiple copies of the same
data.  In this example, the downloaded archives are kept and the extracted files
are dropped.

.. code::

  datalad ukb-update --keyfile <path_to_keyfile> --merge --force --drop extracted

It is also possible to keep the extracted content and drop the archives using
``--drop archives``.
