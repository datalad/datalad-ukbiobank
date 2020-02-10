command_suite = (
    'UKBiobank dataset support',
    [
        (
            'datalad_ukbiobank.init',
            'Init',
            'ukb-init',
            'ukb_init',
        ),
    ]
)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
