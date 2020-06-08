from os.path import join as opj
from datalad.utils import Path
from datalad_ukbiobank.ukb2bids_map import ukb2bids

import logging
lgr = logging.getLogger('datalad.ukbiobank.ukb2bids')


def restructure_ukb2bids(ds, subid, unrecognized_dir, base_path=None):
    """Perform the necessary renames to restructure to BIDS

    Parameters
    ----------
    ds : Dataset
      DataLad dataset instance to restructure. The checked-out branch
      is taken as the subject of restructuring.
    subid : str
      Participant ID
    unrecognized_dir : str or None
      Name of a directory to put all unrecognized files into. The given
      value is used to populate the 'unrecogdir' substitution label
      in `ukb2bids_map`. If None, unrecognized files will not be moved.
      The directory will be placed inside the respective session directory.
    base_path : Path-like
      Base path to determine relative path names of any file for BIDS
      mapping
    """
    # shortcut
    repo = ds.repo

    # prep for yield
    res = dict(
        action='ukb_bidsify',
        type='file',
        logger=lgr,
        refds=ds.path,
    )

    # loop over all known files
    for fp in ds.status(
            path=base_path,
            annex=None,
            untracked='all',
            eval_subdataset_state='no',
            report_filetype='raw',
            return_type='generator',
            result_renderer=None):
        path = Path(fp['path'])
        if not path.exists():
            lgr.debug('Skip mapping %s, no longer exists (likely moved before)', path)
            continue
        rp_parts = list(Path(fp['path']).relative_to(base_path or ds.pathobj).parts)
        # instance number will serve as BIDS session
        try:
            session = rp_parts[0].split('_')[1]
        except IndexError:
            # ignore anything that doesn't look like a UKB data record
            continue
        # pull out instance number from the top-level component, because the matching
        # is uniform and agnostic of instances
        rp_parts[0] = '_'.join(rp_parts[0].split('_')[::2])
        fname = Path(rp_parts[-1])
        # build a list of candidate mapping to try, and suffixes to reappend
        # upon a successful match
        cands = [
            # full thing
            (str(Path(*rp_parts)), ''),
            # without suffix(es)
            (str(Path(
                *rp_parts[:-1],
                fname.name[:-sum(len(s) for s in fname.suffixes)])),
             ''.join(fname.suffixes)),
        ]
        # all intermediate path components
        cands += reversed([
            (str(Path(*rp_parts[:i + 1])),
             str(Path(*rp_parts[i + 1:])))
            for i in range(len(rp_parts) - 1)
        ])
        for pattern, suffix in cands:
            target_path = ukb2bids.get(pattern, None)
            if target_path is not None:
                # append suffix
                if isinstance(suffix, Path):
                    target_path = opj(str(target_path), suffix)
                else:
                    target_path = target_path + suffix
                # apply substitutions
                target_path = target_path.format(
                    subj=subid,
                    session='ses-{}'.format(session),
                    unrecogdir='@@UNRECOG@@'
                    if unrecognized_dir is None
                    else Path('ses-{}'.format(session)) / unrecognized_dir,
                )
                break
        if target_path is None or '@@UNRECOG@@' in target_path:
            yield dict(
                res,
                path=fp['path'],
                status='impossible',
                message='No BIDS file name mapping available',
            )
            continue
        full_sourcepath = Path(fp['path'])
        full_targetpath = ds.pathobj / target_path
        if full_targetpath.exists():
            lgr.info('Overwriting %s', str(target_path))
            target_path.unlink()
        else:
            # ensure target directory
            full_targetpath.parent.mkdir(parents=True, exist_ok=True)
        full_sourcepath.rename(full_targetpath)
        # delete empty source directories
        for p in full_sourcepath.parents:
            try:
                p.rmdir()
            except OSError:
                lgr.debug(
                    "Not removing non-empty parent directory of %s",
                    fp['path'])
                break
        yield dict(
            res,
            path=fp['path'],
            bids_path=str(full_targetpath),
            status='ok',
        )
