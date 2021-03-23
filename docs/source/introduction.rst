.. _chap_introduction:

Introduction
************
This software is a `DataLad <http://datalad.org>`_ extension that equips
DataLad with a set of commands to obtain, monitor, and restructure imaging data
releases of the UK Biobank. It is designed to download MRI bulk data, track
additions/redactions/fixes from the UK Biobank, and (optionally) restructure
into BIDS layout.

What is the UK Biobank?
-----------------------
The `UK Biobank <https://www.ukbiobank.ac.uk>`_ is a national and international
health resource with unparalleled research opportunities, open to all bona fide
health researchers. The UK Biobank aims to improve the prevention, diagnosis and
treatment of a wide range of serious and life-threatening illnesses --- including
cancer, heart diseases, stroke, diabetes, arthritis, osteoporosis, eye
disorders, depression, and forms of dementia. It is following the health and
well-being of 500,000 volunteer participants, and aims to collect imaging
data for 100,000 of the participants. It provides health information, which does
not identify participants, to approved researchers in the UK and overseas, from
academia and industry.

Requirements
------------
In order to download data from the UK Biobank with ``datalad-ukbiobank``, you
will need the following:

* Approved access to download the UK Biobank data. This can be gained as the
  Principal Investigator (PI) on an approved `application <https://www.ukbiobank.ac.uk/register-apply/>`_,
  or as a collaborator with "delegate" status.
* A `keyfile <https://biobank.ndph.ox.ac.uk/showcase/refer.cgi?id=667>`_ (file
  containing a 64-character password that is provided by the UK Biobank after a
  successful application)
* A bulk data file (requires the download of the main dataset and conversion to
  a bulk file; see the UK Biobank `accessing data guide <https://biobank.ndph.ox.ac.uk/showcase/exinfo.cgi?src=AccessingData>`_)
* The `ukbfetch <https://biobank.ctsu.ox.ac.uk/showcase/download.cgi>`_ commandline tool

Installation
------------
The easiest way to install the latest version of ``datalad-ukbiobank`` is from
PyPi. It is recommended to use a dedicated virtual environment:

.. code::

  # create and enter a new virtual environment (optional)
  python3 -m venv ~/.venvs/datalad
  source ~/.venvs/datalad/bin/activate

  # install from PyPi
  pip install datalad_ukbiobank

