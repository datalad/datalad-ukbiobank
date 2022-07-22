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
import shutil

from datalad.interface.base import Interface
from datalad.interface.utils import eval_results
from datalad.interface.base import build_doc
from datalad.interface.add_archive_content import AddArchiveContent
from datalad.support.constraints import (
    EnsureChoice,
    EnsureStr,
    EnsureNone,
)
from datalad.support.param import Parameter
from datalad.support.exceptions import CommandError
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
            doc="""merge any updates into the active branch. If a BIDS layout
            is maintained in the dataset (incoming-bids branch) it will be
            merged into the active branch, the incoming-native branch
            otherwise.
            """),
        force=Parameter(
            args=('-f', '--force',),
            action='store_true',
            doc="""update the incoming branch(es), even if (re-)download
            did not yield changed content (can be useful when restructuring
            setup has changed)."""),
        drop=Parameter(
            args=('--drop',),
            doc="""Drop file content to avoid storage duplication.
            'extracted': drop all content of files extracted from downloaded
            archives to yield the most compact storage at the cost of partial
            re-extraction when accessing archive content;
            'archives': keep extracted content, but drop archives instead.
            By default no content is dropped, duplicating archive content in
            extracted form.""",
            constraints=EnsureChoice(None, 'extracted', 'archives')),

    )
    @staticmethod
    @datasetmethod(name='ukb_update')
    @eval_results
    def __call__(keyfile=None, merge=False, force=False, drop=None,
                 dataset=None):
        ds = require_dataset(
            dataset, check_installed=True, purpose='update')

        if drop and drop not in ('extracted', 'archives'):
            raise ValueError(
                "Unrecognized value for 'drop' option: {}".format(drop))

        repo = ds.repo
        if not keyfile:
            # will error out, if no config was given
            keyfile = repo.config.obtain(
                'datalad.ukbiobank.keyfile',
                dialog_type='question',
                title='Key file location',
                text='Where is the location of the file with the UKB access key?',
            )

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
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            raise RuntimeError(
                "Cannot execute 'ukbfetch'. Original error: {}".format(e))

        # just to be nice, and to be able to check it out again,
        # when we are done
        initial_branch = repo.get_active_branch()

        # make sure we are in incoming, this should create a local branch
        # tracking the remote
        repo.call_git(['checkout', 'incoming'])
        initial_incoming = repo.get_hexsha('incoming')

        # first wipe out all prev. downloaded zip files so we can detect
        # when some files are no longer available
        for fp in repo.pathobj.glob('[0-9]*_[0-9]*_[0-9]_[0-9].*'):
            fp.unlink()

        # a place to put the download logs
        # better be semi-persistent to ease inspection
        tmpdir = repo.pathobj / repo.get_git_dir(repo) / 'tmp' / 'ukb'
        tmpdir.mkdir(parents=True, exist_ok=True)

        # redownload, run with explicit mode, because we just deleted the
        # ZIP files and that is OK
        ds.run(
            cmd='ukbfetch -v -a{} -b.ukbbatch -o{}'.format(
                quote_cmdlinearg(keyfile),
                # use relative path to tmpdir to avoid leakage
                # of system-specific information into the run record
                quote_cmdlinearg(str(tmpdir.relative_to(repo.pathobj))),
            ),
            explicit=True,
            outputs=['.'],
            message="Update from UKBiobank",
        )

        # TODO what if something broke before? needs force switch
        if not force and repo.get_hexsha() == initial_incoming:
            yield dict(
                res,
                status='notneeded',
                message='No new content available',
            )
            repo.call_git(['checkout', initial_branch])
            # TODO drop?
            return

        # onto extraction and transformation of downloaded content
        repo.call_git(['checkout', 'incoming-native'])

        # mark the incoming change as merged
        # (but we do not actually want any branch content)
        repo.call_git(['merge', 'incoming', '--strategy=ours'])

        for fp in repo.get_content_info(
			ref='incoming-native'):
            if fp.name.startswith('.git') \
                    or fp.name.startswith('.datalad') \
                    or fp.name.startswith('.ukb'):
                # skip internals
                continue
            fp.unlink()

        # discover all files present in the last commit in 'incoming'
        for fp, props in repo.get_content_annexinfo(
                ref='incoming', eval_availability=False).items():
            if fp.name.startswith('.git') \
                    or fp.name.startswith('.datalad') \
                    or fp.name.startswith('.ukb'):
                # skip internals
                continue
            # we have to extract into per-instance directories, otherwise files
            # would conflict
            ids = fp.stem.split('_')
            if not len(ids) >= 3:
                raise RuntimeError('Unrecognized filename structure: {}'.format(fp))
            # build an ID from the data record and the array index
            rec_id = '_'.join(ids[1:])

            if fp.suffix == '.zip':
                extract_dir = repo.pathobj / rec_id
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
            else:
                # move into instance dir, and strip participant ID, and instance ID
                # but keep array index
                # e.g. -> 25747_3_0.adv -> instance-3/25747_0
                repo.call_git([
                    'annex', 'fromkey', props['key'],
                    str(repo.pathobj / (rec_id + ''.join(fp.suffixes)))])

        # save whatever the state is now, `save` will discover deletions
        # automatically and also commit them -- wonderful!
        ds.save(message="Update native layout")
        yield dict(
            res,
            status='ok',
        )

        want_bids = 'incoming-bids' in repo.get_branches() \
            or any(b.endswith('/incoming-bids') for b in repo.get_remote_branches())
        if want_bids:
            repo.call_git(['checkout', 'incoming-bids'])
            # mark the incoming change as merged
            # (but we do not actually want any branch content)
            repo.call_git(['merge', 'incoming', '--strategy=ours'])
            # prepare the worktree to match the latest state
            # of incoming-native but keep histories separate
            # (ie. no merge), because we cannot handle partial
            # changes
            repo.call_git(['read-tree', '-u', '--reset', 'incoming-native'])
            # unstage change to present a later `datalad save` a single
            # changeset to be saved (otherwise it might try to keep staged
            # content staged und only save additional modifications)
            #repo.call_git(['restore', '--staged', '.'])
            repo.call_git(['reset', 'HEAD', '.'])

            # and now do the BIDSification
            from datalad_ukbiobank.ukb2bids import restructure_ukb2bids
            # get participant ID from batch file
            subid = list(repo.call_git_items_(
                ["cat-file", "-p", "incoming:.ukbbatch"])
            )[0].split(maxsplit=1)[0]

            yield from restructure_ukb2bids(
                ds,
                subid=subid,
                unrecognized_dir='non-bids',
                base_path=repo.pathobj,
            )
            ds.save(message="Update BIDS layout")

        if drop:
            # None by default to serve as indicator whether we actually want to
            # drop, after checks below
            drop_opts = None
            if drop == 'archives':
                # we need to force the drop, because the download is the
                # only copy we have in general
                drop_opts = ['--force', '--branch', 'incoming', '-I', '*.zip']
            # drop == 'extracted':
            # we would need to drop from the 'archived' special remote. however
            # only if there ever were any archives added we have such a special
            # remote. hence we need to check for existence to avoid a crash
            # https://github.com/datalad/datalad-ukbiobank/issues/69
            elif 'datalad-archives' in [
                    r.get('name') for r in repo.get_special_remotes().values()]:
                drop_opts=['--in', 'datalad-archives',
                           '--branch', 'incoming-native']

            # only if we found drop actually necessary
            if drop_opts:
                for rec in repo.call_annex_records(['drop'] + drop_opts):
                    if not rec.get('success', False):
                        yield dict(
                            action='drop',
                            status='error',
                            message=rec.get('note', 'could not drop key'),
                            key=rec.get('key', None),
                            type='key',
                            path=ds.path,
                        )

        if not merge:
            return

        # and update active branch
        repo.call_git(['checkout', initial_branch])

        if initial_branch in ('incoming',
                              'incoming-native',
                              'incoming-bids'):
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
            'incoming-bids' if want_bids else 'incoming-native'])

        yield dict(
            res,
            action='ukb_merge_update',
            status='ok',
        )
        return
