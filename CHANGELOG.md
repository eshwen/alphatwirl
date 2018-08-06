# Changelog

## [Unreleased]

[diff from the previous release](https://github.com/alphatwirl/alphatwirl/compare/v0.18.6...master)

- changed behavior of `RoundLog`
    - returns the underflow bin for `0` and negative values if `min`
      is given. (previously, returns `0` for `0` and `None` for a
      negative number even when `min` is given)
    - returns the overflow bin for `inf` if `max` is given.
      (previously, returns `None` for `inf` even when `max` is given)
- optimized `RoundLog` and `Round` for speed, e.g., replacing linear
  search with binary search
- updated zenodo badge, using all-versions badge
- added CHANGELOG.md

## [0.18.6] - 2018-08-05

[diff from the previous release](https://github.com/alphatwirl/alphatwirl/compare/v0.18.5...v0.18.6)

- fixed Read The Docs. [\#47](https://github.com/alphatwirl/alphatwirl/issues/40)
- updated README.md
- updated travis-ci config
- updated unittests