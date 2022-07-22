from zipfile import ZipFile

from datalad.utils import Path


# structural sketch of data record content
records = {
    '25747_2_0.adv': '25747_2_0.adv',
    '25748_2_0.txt': '25748_2_0.txt',
    '25748_3_0.txt': '25748_3_0.txt',
    '20227_2_0': {
        'fMRI': {
            'rfMRI.nii.gz': 'rfMRI.nii.gz',
            'rfMRI_SBREF.nii.gz': 'rfMRI_SBREF.nii.gz',
            'rfMRI.json': 'rfMRI.json',
            'rfMRI_SBREF.json': 'rfMRI_SBREF.json',
            'rfMRI.ica': {
                '.files': {
                    'fsl.css': 'fsl.css',
                },
                'images': {
                    'fsl-bg.jpg': 'fsl-bg.jpg',
                    'fsl-logo-big.jpg': 'fsl-logo-big.jpg',
                },
                'design.fsf': 'design.fsf',
            },
        },
    },
}


def _put_in_zip(zip, path, records):
    for k, v in records.items():
        if isinstance(v, dict):
            _put_in_zip(zip, path + [k],  v)
        else:
            zip.writestr(str(Path(*path) / k), v)


# pre-fill dst with the simple things
def make_datarecord_zips(subid, dst):
    for k, v in records.items():
        if '.' in k:
            (Path(dst) / '{}_{}'.format(subid, k)).write_text(v)
        else:
            with ZipFile(
                    str(Path(dst) / '{}_{}.zip'.format(subid, k)), 'w') as z:
                _put_in_zip(z, ['.'], v)
