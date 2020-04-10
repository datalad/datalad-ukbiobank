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
import subprocess

from datalad.interface.base import Interface
from datalad.interface.utils import eval_results
from datalad.interface.base import build_doc
from datalad.interface.add_archive_content import AddArchiveContent
from datalad.support.constraints import (
    EnsureStr,
    EnsureNone,
)
from datalad.support.param import Parameter
from datalad.utils import (
    chpwd,
    quote_cmdlinearg,
    Path,
)

from datalad.distribution.dataset import (
    datasetmethod,
    EnsureDataset,
    require_dataset,
)


__docformat__ = 'restructuredtext'

lgr = logging.getLogger('datalad.ukbiobank.update')


@build_doc
class Update(Interface):
    """Update an existing dataset of a UKbiobank participant

    This command expects an ukb-init initialized DataLad dataset. The dataset
    may or may not have any downloaded content already.

    Downloads are performed with the `ukbfetch` tool, which is expected to
    be available and executable.
    """

    _params_ = dict(
        dataset=Parameter(
            args=("-d", "--dataset"),
            metavar='DATASET',
            doc="""specify the dataset to perform the initialization on""",
            constraints=EnsureDataset() | EnsureNone()),
        keyfile=Parameter(
            args=('-k', '--keyfile',),
            metavar='PATH',
            doc="""path to a file with an authentification key
            (ukbfetch -a ...). If none is given, the configuration
            datalad.ukbiobank.keyfile is consulted.""",
            constraints=EnsureStr() | EnsureNone()),
        merge=Parameter(
            args=('--merge',),
            action='store_true',
            doc="""merge any updates into the active branch
            """),
        force_update=Parameter(
            args=('--force-update',),
            action='store_true',
            doc="""update the incoming-processed branch, even if (re-)download
            did not yield changed content (can be useful when restructuring
            setup has changed)."""),
        bids=Parameter(
            args=('--bids',),
            action='store_true',
            doc="""restructure the incoming-processed branch into a BIDS-like
            organization."""),
        non_bids_dir=Parameter(
            args=('--non-bids-dir',),
            metavar='PATH',
            doc="""if BIDS restructuring is enabled, relative path (to the
            session directory) of a directory to place all unrecognized files
            into.""",
            constraints=EnsureStr() | EnsureNone()),
    )
    @staticmethod
    @datasetmethod(name='ukb_update')
    @eval_results
    def __call__(keyfile=None, merge=False, force_update=False, bids=False,
                 non_bids_dir='non-bids', dataset=None):
        ds = require_dataset(
            dataset, check_installed=True, purpose='update')

        repo = ds.repo
        if not keyfile:
            # will error out, if no config was given
            keyfile = repo.config.obtain('datalad.ukbiobank.keyfile')

        # prep for yield
        res = dict(
            action='ukb_update',
            path=ds.path,
            type='dataset',
            logger=lgr,
            refds=ds.path,
        )

        if repo.dirty:
            yield dict(
                res,
                status='error',
                message="Refuse to operate on dirty dataset",
            )
            return

        # check if we have 'ukbfetch' before we start fiddling with the dataset
        # and leave it in a mess for no reason
        try:
            subprocess.run(
                # pull version info
                ['ukbfetch', '-i'],
                capture_output=True,
            )
        except Exception as e:
            raise RuntimeError(
                "Cannot execute 'ukbfetch'. Original error: {}".format(e))

        # just to be nice, and to be able to check it out again,
        # when we are done
        initial_branch = repo.get_active_branch()
        initial_incoming = repo.get_hexsha('incoming')

        # make sure we are in incoming
        repo.call_git(['checkout', 'incoming'])

        # first wipe out all prev. downloaded zip files so we can detect
        # when some files are no longer available
        for zp in repo.pathobj.glob('*.zip'):
            zp.unlink()

        # a place to put the download logs
        # better be semi-persistent to ease inspection
        tmpdir = repo.pathobj / repo.get_git_dir(repo) / 'tmp' / 'ukb'
        tmpdir.mkdir(parents=True, exist_ok=True)

        # redownload, run with explicit mode, because we just deleted the
        # ZIP files and that is OK
        ds.run(
            cmd='ukbfetch -v -a{} -b.ukbbatch -o{}'.format(
                quote_cmdlinearg(keyfile),
                quote_cmdlinearg(str(tmpdir)),
            ),
            explicit=True,
            outputs=['.'],
            message="Update from UKbiobank",
        )

        # TODO what if something broke before? needs force switch
        if not force_update and repo.get_hexsha() == initial_incoming:
            yield dict(
                res,
                status='notneeded',
                message='No new content available',
            )
            repo.call_git(['checkout', initial_branch])
            # TODO drop?
            return

        # onto extraction and transformation of downloaded content
        repo.call_git(['checkout', 'incoming-processed'])

        # mark the incoming change as merged
        # (but we do not actually want any branch content)
        repo.call_git(['merge', 'incoming', '--strategy=ours', 'incoming'])

        for fp in repo.get_content_info(
                ref='incoming-processed',
                eval_file_type=False):
            fp.unlink()

        subid = None
        if bids:
            from datalad_ukbiobank.ukb2bids import restructure_ukb2bids
            # get participant ID from batch file
            subid = list(repo.call_git_items_(
                ["cat-file", "-p", "incoming:.ukbbatch"])
            )[0].split(maxsplit=1)[0]

        # discover all zip files present in the last commit in 'incoming'
        for fp, props in repo.get_content_annexinfo(
                ref='incoming', eval_availability=False).items():
            if fp.suffix != '.zip':
                continue
            # we have to extract into per-instance directories, otherwise files
            # would conflict
            ids = fp.stem.split('_')
            if not len(ids) >= 3:
                raise RuntimeError('Unrecognized filename structure: {}'.format(fp))
            extract_dir = repo.pathobj / 'instance-{}'.format(ids[2])
            extract_dir.mkdir(exist_ok=True)

            with chpwd(extract_dir):
                # extract and add their content
                AddArchiveContent.__call__(
                    props['key'],
                    key=True,
                    annex=repo,
                    # --use-current-dir due to
                    # https://github.com/datalad/datalad/issues/3995
                    use_current_dir=True,
                    allow_dirty=True,
                    commit=False,
                )

            if bids:
                yield from restructure_ukb2bids(
                    ds,
                    subid=subid,
                    unrecognized_dir=Path('ses-{}'.format(ids[2])) / non_bids_dir,
                    base_path=extract_dir,
                    session=ids[2],
                )

        # save whatever the state is now, `save` will discover deletions
        # automatically and also commit them -- wonderful!
        ds.save(message="Track ZIP file content")
        yield dict(
            res,
            status='ok',
        )

        if not merge:
            return

        # and update active branch
        repo.call_git(['checkout', initial_branch])

        if initial_branch in ('incoming', 'incoming-processed'):
            yield dict(
                res,
                action='ukb_merge_update',
                status='impossible',
                message='Refuse to merge into incoming* branch',
            )
            return

        repo.call_git([
            'merge',
            '-m', "Merge update from UKbiobank",
            'incoming-processed'])

        yield dict(
            res,
            action='ukb_merge_update',
            status='ok',
        )
        return
