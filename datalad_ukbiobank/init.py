# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""

"""

import logging

from datalad.interface.base import Interface
from datalad.interface.utils import eval_results
from datalad.interface.base import build_doc
from datalad.support.constraints import (
    EnsureStr,
    EnsureNone,
)
from datalad.support.param import Parameter
from datalad.utils import (
    ensure_list,
)

from datalad.distribution.dataset import (
    datasetmethod,
    EnsureDataset,
    require_dataset,
)


__docformat__ = 'restructuredtext'

lgr = logging.getLogger('datalad.ukbiobank.init')


@build_doc
class Init(Interface):
    """Initialize an existing dataset to track a UKBiobank participant

    A batch file for the 'ukbfetch' tool will be generated and placed into the
    dataset. By selecting the relevant data records, raw and/or preprocessed
    data will be tracked.

    After initialization the dataset will contain at least three branches:

    - incoming: to track the pristine ZIP files downloaded from UKB
    - incoming-processed: to track extracted ZIP file content, in a potentially
      restructures layout (i.e. BIDS-like file name conventions)
    - master: based off of incoming-processed with potential manual modifications
      applied
    """

    _examples_ = [
        dict(
            text='Initialize a dataset in the current directory',
            code_cmd='datalad ukb-init 5874415 20227_2_0 20249_2_0',
            code_py='ukb_init(participant="5874415", records=["20227_2_0", "20249_2_0"])'),
    ]

    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            metavar='DATASET',
            doc="""specify the dataset to perform the initialization on""",
            constraints=EnsureDataset() | EnsureNone()),
        participant=Parameter(
            args=('participant',),
            metavar='PARTICPANT-ID',
            nargs=1,
            doc="""UKBiobank participant ID to use for this dataset
            (note: these encoded IDs are unique to each
            application/project)""",
            constraints=EnsureStr()),
        records=Parameter(
            args=('records',),
            metavar='DATARECORD-ID',
            nargs='+',
            doc='One or more data record identifiers',
            constraints=EnsureStr()),
        force=Parameter(
            args=("-f", "--force",),
            doc="""force (re-)initialization""",
            action='store_true'),
    )
    @staticmethod
    @datasetmethod(name='ukb_init')
    @eval_results
    def __call__(participant, records, force=False, dataset=None):
        ds = require_dataset(
            dataset, check_installed=True, purpose='initialization')

        participant = ensure_list(participant)[0]
        records = ensure_list(records)

        repo = ds.repo
        branches = repo.get_branches()

        # prep for yield
        res = dict(
            action='ukb_init',
            path=ds.path,
            type='dataset',
            logger=lgr,
            refds=ds.path,
        )

        if 'incoming' in branches and not force:
            yield dict(
                res,
                status='error',
                message='Dataset found already initialized, '
                        'use `force` to reinitialize',
            )
            return
        if 'incoming' not in branches:
            # establish "incoming" branch that will hold pristine UKB downloads
            repo.call_git(['checkout', '--orphan', 'incoming'])
        else:
            repo.call_git(['checkout', 'incoming'])

        # place batch file with download config for ukbfetch in it
        batchfile = repo.pathobj / '.ukbbatch'
        batchfile.write_text(
            '{}\n'.format(
                '\n'.join(
                    '{} {}'.format(
                        participant,
                        rec)
                    for rec in records)
            )
        )
        # save to incoming branch, provide path to avoid adding untracked
        # content
        ds.save(
            path='.ukbbatch',
            to_git=True,
            message="Configure UKB data fetch",
            result_renderer=None,
        )
        # establish rest of the branch structure: "incoming-processsed"
        # for extracted archive content
        if 'incoming-processed' not in branches:
            repo.call_git(['checkout', '-b', 'incoming-processed'])
        else:
            repo.call_git(['checkout', 'incoming-processed'])
            # the only thing that we changed in 'incoming' is the batchfile
            # which we will wipe out from 'incoming-processed' below.
            # use -s ours to avoid merge conflicts due to the deleted
            # file
            repo.call_git(['merge', 'incoming', '-s', 'ours'])
        # wipe out batch file to keep download-related info separate
        if batchfile.exists():
            repo.call_git_success(['rm', '-f', '.ukbbatch'])
            repo.commit(
                files=['.ukbbatch'],
                msg="Do not leak ukbfetch configuration into dataset content")
        # force merge unrelated histories into master
        # we are using an orphan branch such that we know that
        # `git ls-tree incoming`
        # will only report download-related content, nothing extracted or
        # manually modified
        repo.call_git(['checkout', 'master'])
        repo.call_git([
            'merge',
            '-m', 'Merge incoming',
            '--allow-unrelated-histories',
            'incoming-processed',
        ])

        yield dict(
            res,
            status='ok',
            participant=participant,
            records=records,
        )
        return
