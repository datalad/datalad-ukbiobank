# DataLad extension for working with the UKbiobank

[![GitHub release](https://img.shields.io/github/release/datalad/ukbiobank.svg)](https://GitHub.com/datalad/ukbiobank/releases/) [![PyPI version fury.io](https://badge.fury.io/py/ukbiobank.svg)](https://pypi.python.org/pypi/ukbiobank/)

This software is a [DataLad](http://datalad.org) extension that equips DataLad
with a set of commands to obtain (and monitor) imaging data releases of the
UKbiobank.

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

