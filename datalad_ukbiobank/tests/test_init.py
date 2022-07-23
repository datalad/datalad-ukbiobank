from datalad.api import (
    create,
    ukb_init,
)
from datalad.tests.utils_pytest import (
    assert_not_in,
    assert_status,
    assert_true,
    DEFAULT_BRANCH,
    eq_,
    with_tempfile,
)

ckwa = dict(
    result_renderer='disabled',
)


@with_tempfile
def test_base(path=None):
    ds = create(path, **ckwa)
    ds.ukb_init('12345', ['20249_2_0', '20249_3_0', '20250_2_0'], **ckwa)
    # standard branch setup
    assert_true(all(
        b in sorted(ds.repo.get_branches())
        for b in ['git-annex', 'incoming', 'incoming-native', DEFAULT_BRANCH])
    )
    # standard batch file setup
    eq_(ds.repo.call_git(['cat-file', '-p', 'incoming:.ukbbatch']),
        '12345 20249_2_0\n12345 20249_3_0\n12345 20250_2_0\n')
    # intermediate branch is empty, apart from .gitattributes
    eq_([l
         for l in ds.repo.call_git(['ls-tree', 'incoming-native']).splitlines()
         if not l.strip().endswith('.gitattributes')],
        [])
    # no batch in master
    assert_not_in('ukbbatch', ds.repo.call_git(['ls-tree', DEFAULT_BRANCH]))

    # no re-init without force
    assert_status(
        'error',
        ds.ukb_init('12', ['12', '23'], on_failure='ignore', **ckwa))

    ds.ukb_init('12345', ['20250_2_0'], force=True, **ckwa)
    eq_(ds.repo.call_git(['cat-file', '-p', 'incoming:.ukbbatch']),
        '12345 20250_2_0\n')


@with_tempfile
def test_bids(path=None):
    ds = create(path)
    ds.ukb_init('12345', ['20249_2_0', '20249_3_0', '20250_2_0'],
                bids=True, **ckwa)
    # standard branch setup
    assert_true(all(
        b in sorted(ds.repo.get_branches())
        for b in ['git-annex', 'incoming', 'incoming-native', DEFAULT_BRANCH])
    )
    # intermediate branches are empty
    for b in 'incoming-bids', 'incoming-native':
        eq_([l
             for l in ds.repo.call_git(['ls-tree', b]).splitlines()
             if not l.strip().endswith('.gitattributes')],
            [])
    # no batch in master
    assert_not_in('ukbbatch', ds.repo.call_git(['ls-tree', DEFAULT_BRANCH]))

    # smoke test for a reinit
    ds.ukb_init('12345', ['20250_2_0'], bids=True, force=True, **ckwa)
    assert_true(all(
        b in sorted(ds.repo.get_branches())
        for b in ['git-annex', 'incoming', 'incoming-native',
                  'incoming-bids', DEFAULT_BRANCH])
    )
