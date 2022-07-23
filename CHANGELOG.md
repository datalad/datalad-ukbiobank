0.3.4 (Jul 23, 2021) -- pytest with little bits and pieces

- The documentation was extended with information on the
  `ukbfetch` dependency, and on `ukbfetch_surrogate`.

- Various bits of the code have been adjusted for changes in
  DataLad (with no implied change of functionality).

- The test battery has been ported to `pytest` (95% coverage).

0.3.3 (May 19, 2021) -- drop fix

- Fixes

  - check whether there is a `datalad-archives` special remote,
    before attempting to drop from it. Before, the `ukb-update`
    would crash for datatype collections that do not contain
    any archive. gh-69

0.3.2 (Mar 23, 2021) -- docs!

- Major documentation update: concepts, procedures, commands

- Fixes

  - Improved maintainability. `ukb-update` now runs on a fresh clone
    of a dataset that has been initialized with `ukb-init` in the past.
    gh-55

  - All branches processed by `ukb-update` will now inherit the most
    recent state of the main branch's `.gitattributes` file. gh-54

  - No longer hard-code the name of the main branch. gh-68

0.3.1 (Jan 27, 2021) -- just fiddling

- Minor adjustments for compatibility with DataLad 0.14

0.3 (Jun 15, 2020) -- break for good

- Various substantial issues were fixed:

  - Handle non-ZIP file download properly.

  - Avoid leakage of absolute paths into the run-record for `ukbfetch`.

  - Establish a new "native" layout for (extracted) data records that
    makes it possible to properly associate individual files with their
    records, even when an original archive does not contain a top-level
    directory. gh-29

  - Updated BIDS file name mapping.

- A "native" (`incoming-native` branch) and a "bids" layout (`incoming-bids`
  branch) are now maintained in parallel by `ukb-update` to support both views
  using a single dataset. Enabling the "bids" layout is now done via `ukb-init`.
  gh-38

- Added Sphinx-based documentation available at:
  http://docs.datalad.org/projects/ukbiobank

- `ukb-update --force-update` was renamed to `ukb-update --force`.

- The `ukb-update` option `--no-bids-dir` was removed.

- `ukb-update` learned to optionally drop extracted archive content or
  downloaded archives (`--drop`). Both modes avoid duplication of storage.

- A basic usage description was added to the README.

- A unit test battery was added.

- A keyfile location can now be entered interactively, if not pre-configured.
  gh-39

- An example implementation of a faux `ukbfetch` is now included in `tools/`.
  Such an implementation can be used to feed already downloaded UKB data
  records to this extension.

0.2 (Apr 11, 2020) -- multi-utility

- Support for multi-instance data records (i.e. imaging data from multiple
  visits). Data is now organized into `instance-?/` subdirectories, where `?`
  is the instance ID (e.g. 2 or 3). In BIDS layout the same IDs are used as
  'session' identifiers. Data are now unconditionally grouped by
  instance/session, even if no multi-instance data is present yet, in order to
  improve forward-compatibility with future UKB updates.

- Availability of `ukbfetch` is now tested at the start of `ukb-update` to
  prevent a dirty crash during processing.

- Prevent crash of `ukb-init` with a different set of record IDs.

- Fix log setup to make user-targeted messages visible.

0.1 (Feb 13, 2020) -- don't touch this

- Initial draft implementation
