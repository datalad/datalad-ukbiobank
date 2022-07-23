# DataLad extension for working with the UKbiobank

[![GitHub release](https://img.shields.io/github/release/datalad/ukbiobank.svg)](https://GitHub.com/datalad/ukbiobank/releases/) [![PyPI version fury.io](https://badge.fury.io/py/datalad-ukbiobank.svg)](https://pypi.python.org/pypi/datalad-ukbiobank/) [![Build status](https://ci.appveyor.com/api/projects/status/2oud5x4cvfhu9wxk/branch/main?svg=true)](https://ci.appveyor.com/project/mih/datalad-ukbiobank/branch/main) [![codecov.io](https://codecov.io/github/datalad/datalad-ukbiobank/coverage.svg?branch=main)](https://codecov.io/github/datalad/datalad-ukbiobank?branch=main) [![Documentation Status](https://readthedocs.org/projects/datalad-ukbiobank/badge/?version=latest)](http://docs.datalad.org/projects/ukbiobank/en/latest/?badge=latest) [![DOI](https://zenodo.org/badge/220525829.svg)](https://zenodo.org/badge/latestdoi/220525829)


This software is a [DataLad](http://datalad.org) extension that equips DataLad
with a set of commands to obtain (and monitor) imaging data releases of the
UKbiobank (see [documentation](http://docs.datalad.org/projects/ukbiobank) for
more information).

[UKbiobank](https://www.ukbiobank.ac.uk) is a national and international health
resource with unparalleled research opportunities, open to all bona fide health
researchers. UK Biobank aims to improve the prevention, diagnosis and treatment
of a wide range of serious and life-threatening illnesses – including cancer,
heart diseases, stroke, diabetes, arthritis, osteoporosis, eye disorders,
depression and forms of dementia. It is following the health and well-being of
500,000 volunteer participants and provides health information, which does not
identify them, to approved researchers in the UK and overseas, from academia
and industry.

Command(s) provided by this extension

- `ukb-init` -- Initialize an existing dataset to track a UKBiobank participant
- `ukb-update` -- Update an existing dataset of a UKbiobank participant

## Installation

Before you install this package, please make sure that you [install a recent
version of git-annex](https://git-annex.branchable.com/install).  Afterwards,
install the latest version of `datalad-ukbiobank` from
[PyPi](https://pypi.org/project/datalad-ukbiobank). It is recommended to use
a dedicated [virtualenv](https://virtualenv.pypa.io):

    # create and enter a new virtual environment (optional)
    virtualenv --system-site-packages --python=python3 ~/env/datalad
    . ~/env/datalad/bin/activate

    # install from PyPi
    pip install datalad_ukbiobank

You will also need to download the `ukbfetch` utility provided by the UK
Biobank. See the [ukbfetch documentation](https://biobank.ctsu.ox.ac.uk/showcase/refer.cgi?id=644)
for specifics.

## Use

To track UKB data for a single participant (example ID: 1234), start by
creating and initializing a new dataset:

```
% datalad create 1234
% cd 1234
% datalad ukb-init --bids 1234 20227_2_0 20227_3_0 25755_2_0 25755_3_0
```

In this example only two data records with two instances each are selected.
However, any other selection is supported too. The `--bids` flag enables
an additional dataset layout with a BIDS-like structure.

After initialization, run `ukb-update` at any time to (re-)download data
from UKB, and update the dataset in order to track changes longitudinally.

```
datalad -c datalad.ukbiobank.keyfile=<pathtoaccesstoken> ukb-update
```

This will maintain two or three branches:

- `incoming`: tracking the pristine UKB downloads
- `incoming-native`: a "native" representation of the extracted downloads
  for single file access using UKB naming conventions
- `incoming-bids`: an alternative dataset layout using BIDS conventions
  (if enabled with `ukb-init --bids`)

Changes can then be merged manually into the main branch. Alternatively,
`ukb-update --merge` merges `incoming-native` (or `incoming-bids` if enabled)
automatically.


## Use with pre-downloaded data

Re-download can be avoided (while maintaining all other functionality), if the
`ukbfetch` utility is replaced by a shim that obtains the relevant files from
where they have been downloaded to. An example script is provided at
`tools/ukbfetch_surrogate.sh`.

One simple way to use this script is to add a symlink at `~/env/datalad/bin/` for example:
```
ln -s tools/ukbfetch_surrogate.sh ~/env/datalad/bin/ukbfetch`
```

## Use on non-UNIX-like operating systems

This code relies on a number of POSIX filesystem features that may make it
somewhat hard to get working on Windows. Contributions to port this extension
to non-POSIX platforms are welcome, but presently this is not supported.


## Support

For general information on how to use or contribute to DataLad (and this
extension), please see the [DataLad website](http://datalad.org) or the
[main GitHub project page](http://datalad.org).

All bugs, concerns and enhancement requests for this software can be submitted here:
https://github.com/datalad/ukbiobank/issues

If you have a problem or would like to ask a question about how to use DataLad,
please [submit a question to
NeuroStars.org](https://neurostars.org/tags/datalad) with a ``datalad`` tag.
NeuroStars.org is a platform similar to StackOverflow but dedicated to
neuroinformatics.

All previous DataLad questions are available here:
http://neurostars.org/tags/datalad/


## Acknowledgements

This development was supported by European Union’s Horizon 2020 research and
innovation programme under grant agreement [VirtualBrainCloud
(H2020-EU.3.1.5.3, grant no.
826421)](https://cordis.europa.eu/project/id/826421).

