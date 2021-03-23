.. _chap_concepts:

Concepts & Terms
****************
The extension operates on a single UK Biobank subject, and acts as a wrapper
around the ``ukbfetch`` tool to retrieve, ingest, restructure, and update data.
The first command, ``ukb-init``, initializes a dataset for a given UK Biobank
participant and data field(s). The second command, ``ukb-update`` updates a
dataset for the initialized subject/data fields.

Dataset Structure
-----------------
``datalad-ukbiobank`` allows for only one subject per dataset. Tailored or
comprehensive superdatasets can then be created to link the desired subject
datasets as subdatasets. This structure keeps each dataset lightweight and
promotes parallel downloads.

Branches
--------
Data can be viewed in different layouts by checking out layout-specific branches:

``incoming``
  the unextracted archives, as downloaded from the UK Biobank (e.g. zip files)

``incoming-native``
  the extracted files in the original layout provided by the UK Biobank

``incoming-bids``
  if enabled, the extracted files converted to a BIDS(-like) layout

Bulk File
---------
The required *bulk file* lists all participant IDs and data field IDs that are
available for download for an approved application. These participant IDs and
data field IDs are then used as input for the ``ukb-init`` command.

To generate a bulk file, follow the UK Biobank `accessing data guide <https://biobank.ndph.ox.ac.uk/showcase/exinfo.cgi?src=AccessingData>`_
to first download the main dataset and then generate a bulk file. Section 3.2.2
of this document explains how to create modality specific bulk files (e.g.
participant IDs for all those with T1 structural brain images).

Once a bulk file is created, it can be parsed to extract the desired participant
and data field IDs for download with ``datalad-ukbiobank``.

Snippet of a bulk file:

.. code::

  1002532 20227_2_0
  1002532 20227_3_0
  1002532 20249_2_0
  1002532 20249_3_0
  1002532 20250_2_0
  1002532 20250_3_0
  1003339 20251_2_0
  1003339 20251_3_0
  1003339 20252_2_0
  1003339 20252_3_0
  1003339 20253_2_0
  1003339 20253_3_0

Participant ID
  These are unique to each application/project (e.g. 1002532).

Data field IDs
  Indicates the *data type* (e.g. 20227 = NIFTI functional rest image),
  *instance index* (e.g. 2 = first imaging visit), and *array index* (e.g. 0).
  The `instance index <https://biobank.ndph.ox.ac.uk/showcase/instance.cgi?id=2>`_
  distinguishes data that were gathered at different times (sessions). The *array
  index* indicates if multiple pieces of data were gathered at the same time.
  These fields are explained in more detail in section 2.8 of the UK Biobank
  `accessing data guide <https://biobank.ndph.ox.ac.uk/showcase/exinfo.cgi?src=AccessingData>`_

ukbfetch
--------
`ukbfetch <https://biobank.ctsu.ox.ac.uk/showcase/download.cgi>`_ is a tool
provided by the UK Biobank. It downloads specified *bulk data*, and requires
authentication with a `keyfile <https://biobank.ndph.ox.ac.uk/showcase/refer.cgi?id=667>`_.
See the `ukbfetch documentation <https://biobank.ctsu.ox.ac.uk/showcase/refer.cgi?id=644>`_
for specifics.

``datalad-ukbionbank`` downloads data with the ``ukbfetch`` tool (which must be
available in ``PATH``).

The UK Biobank allows multiple downloads in parallel, but limits each
application to 10 concurrent downloads.

.. note::
  If you already have UK Biobank archives downloaded, and want to use
  ``datalad-ukbiobank`` without re-downloading everything, you can simply replace
  ``ukbfetch`` with a `script <https://github.com/datalad/datalad-ukbiobank/blob/master/tools/ukbfetch_surrogate.sh>`_
  to obtain the relevant files from where they are located.
