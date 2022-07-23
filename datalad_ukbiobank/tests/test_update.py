import sys
import os
from unittest.mock import patch

from datalad.api import (
    create,
    clone,
)
from datalad.tests.utils_pytest import (
    assert_in,
    assert_in_results,
    assert_not_in,
    assert_raises,
    assert_status,
    eq_,
    neq_,
    skip_if_on_windows,
    with_tempfile,
)
from datalad_ukbiobank.tests import (
    make_datarecord_zips,
)

ckwa = dict(
    result_renderer='disabled',
)


# code of a fake ukbfetch drop-in
ukbfetch_code = """\
#!{pythonexec}

import shutil
from pathlib import Path

for line in open('.ukbbatch'):
    rec = '_'.join(line.split())
    for ext in ('zip', 'adv', 'txt'):
        testpath = Path('{basepath}', '%s.%s' % (rec, ext))
        if testpath.exists():
            shutil.copyfile(str(testpath), testpath.name)
"""


def make_ukbfetch(ds, records):
    # fake ukbfetch
    bin_dir = ds.pathobj / '.git' / 'tmp'
    bin_dir.mkdir()
    ukbfetch_file = bin_dir / 'ukbfetch'
    ukbfetch_file.write_text(
        ukbfetch_code.format(
            pythonexec=sys.executable,
            basepath=records,
        )
    )
    ukbfetch_file.chmod(0o744)
    return bin_dir


@skip_if_on_windows  # see gh-61
@with_tempfile
@with_tempfile(mkdir=True)
@with_tempfile(mkdir=True)
def test_base(dspath=None, records=None, clonedir=None):
    # make fake UKB datarecord downloads
    make_datarecord_zips('12345', records)

    # init dataset
    ds = create(dspath, **ckwa)
    ds.ukb_init(
        '12345',
        ['20227_2_0', '25747_2_0', '25748_2_0', '25748_3_0'], **ckwa)
    # dummy key file, no needed to bypass tests
    ds.config.add('datalad.ukbiobank.keyfile', 'dummy', where='local')

    # fake ukbfetch
    bin_dir = make_ukbfetch(ds, records)

    # refuse to operate on dirty datasets
    (ds.pathobj / 'dirt').write_text('dust')
    assert_status('error', ds.ukb_update(on_failure='ignore', **ckwa))
    (ds.pathobj / 'dirt').unlink()

    # meaningful crash with no ukbfetch
    assert_raises(RuntimeError, ds.ukb_update)

    # put fake ukbfetch in the path and run
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        ds.ukb_update(merge=True, **ckwa)

    # get expected file layout
    incoming = ds.repo.get_files('incoming')
    incoming_p = ds.repo.get_files('incoming-native')
    for i in ['12345_25748_2_0.txt', '12345_25748_3_0.txt', '12345_20227_2_0.zip']:
        assert_in(i, incoming)
    for i in ['25748_2_0.txt', '25748_3_0.txt', '20227_2_0/fMRI/rfMRI.nii.gz']:
        assert_in(i, incoming_p)
    # not ZIPs after processing
    assert_not_in('12345_20227_2_0.zip', incoming_p)
    assert_not_in('20227_2_0.zip', incoming_p)

    # rerun works
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        ds.ukb_update(merge=True, **ckwa)

    cloned = clone(source=ds.path, path=clonedir, **ckwa)
    cloned.config.add('datalad.ukbiobank.keyfile', 'dummy', where='local')
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        cloned.ukb_update(merge=True, **ckwa)

    # rightfully refuse to merge when active branch is an incoming* one
    ds.repo.checkout('incoming')
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        assert_in_results(
            ds.ukb_update(merge=True, force=True, on_failure='ignore', **ckwa),
            status='impossible',
            message='Refuse to merge into incoming* branch',)


@skip_if_on_windows  # see gh-61
@with_tempfile
@with_tempfile(mkdir=True)
def test_bids(dspath=None, records=None):
    # make fake UKB datarecord downloads
    make_datarecord_zips('12345', records)

    # init dataset
    ds = create(dspath, **ckwa)
    ds.ukb_init(
        '12345',
        ['20227_2_0', '25747_2_0', '25748_2_0', '25748_3_0'],
        bids=True, **ckwa)
    # dummy key file, no needed to bypass tests
    ds.config.add('datalad.ukbiobank.keyfile', 'dummy', where='local')
    bin_dir = make_ukbfetch(ds, records)

    # put fake ukbfetch in the path and run
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        ds.ukb_update(merge=True, **ckwa)

    bids_files = ds.repo.get_files('incoming-bids')
    master_files = ds.repo.get_files()
    for i in [
            'ses-2/func/sub-12345_ses-2_task-rest_bold.nii.gz',
            'ses-2/non-bids/fMRI/sub-12345_ses-2_task-hariri_eprime.txt',
            'ses-3/non-bids/fMRI/sub-12345_ses-3_task-hariri_eprime.txt']:
        assert_in(i, bids_files)
        assert_in(i, master_files)

    # run again, nothing bad happens
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        ds.ukb_update(merge=True, force=True, **ckwa)

    bids_files = ds.repo.get_files('incoming-bids')
    master_files = ds.repo.get_files()
    for i in [
            'ses-2/func/sub-12345_ses-2_task-rest_bold.nii.gz',
            'ses-2/non-bids/fMRI/sub-12345_ses-2_task-hariri_eprime.txt',
            'ses-3/non-bids/fMRI/sub-12345_ses-3_task-hariri_eprime.txt']:
        assert_in(i, bids_files)
        assert_in(i, master_files)

    # now re-init with a different record subset and rerun
    ds.ukb_init('12345', ['25747_2_0', '25748_2_0', '25748_3_0'],
                bids=True, force=True, **ckwa)
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        ds.ukb_update(merge=True, force=True, **ckwa)


@skip_if_on_windows  # see gh-61
@with_tempfile
@with_tempfile(mkdir=True)
def test_drop(dspath=None, records=None):
    make_datarecord_zips('12345', records)
    ds = create(dspath, **ckwa)
    ds.ukb_init(
        '12345',
        ['20227_2_0', '25747_2_0', '25748_2_0', '25748_3_0'], **ckwa)
    ds.config.add('datalad.ukbiobank.keyfile', 'dummy', where='local')
    bin_dir = make_ukbfetch(ds, records)

    # baseline
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        ds.ukb_update(merge=True, force=True, **ckwa)
    zips_in_ds = list(ds.pathobj.glob('**/*.zip'))
    neq_(zips_in_ds, [])

    # drop archives
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        ds.ukb_update(merge=True, force=True, drop='archives', **ckwa)
    # no ZIPs can be found, also not in the annex
    eq_(list(ds.pathobj.glob('**/*.zip')), [])
    # we can get all we want (or rather still have it)
    assert_status('notneeded', ds.get('.', **ckwa))

    # now drop extracted content instead
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        ds.ukb_update(merge=True, force=True, drop='extracted', **ckwa)
    eq_(list(ds.pathobj.glob('**/*.zip')), zips_in_ds)
    # we can get all
    assert_status('ok', ds.get('.', **ckwa))
    # a non-zip content file is still around
    eq_((ds.pathobj / '25747_2_0.adv').read_text(), '25747_2_0.adv')
