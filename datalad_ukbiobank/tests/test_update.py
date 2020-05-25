import sys
import os
from mock import patch

from datalad.api import (
    create,
)
from datalad.tests.utils import (
    with_tempfile,
)
from datalad_ukbiobank.tests import (
    make_datarecord_zips,
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


@with_tempfile
@with_tempfile(mkdir=True)
def test_dummy(dspath, records):
    # make fake UKB datarecord downloads
    make_datarecord_zips('12345', records)

    # init dataset
    ds = create(dspath)
    ds.ukb_init(
        '12345',
        ['20227_2_0', '25747_2_0.adv', '25748_2_0', '25748_3_0'])
    # dummy key file, no needed to bypass tests
    ds.config.add('datalad.ukbiobank.keyfile', 'dummy', where='local')

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

    # put fake ukbfetch in the path and run
    with patch.dict('os.environ', {'PATH': '{}:{}'.format(
            str(bin_dir),
            os.environ['PATH'])}):
        ds.ukb_update()

    # add actual checks
