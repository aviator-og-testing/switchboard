# How evaluation works

Written up after the 2021 incident so the on-call rotation has something to read.

## Order

A flag is evaluated in three steps.

1. Disabled flags short circuit to `default_variant`.
2. Targeting rules run in the order they were created. The first one that
   matches returns its variant and nothing else runs.
3. Anyone left over is bucketed by percentage.

## Bucketing

The bucket is the sum of the bytes of the flag key and the user id, modulo 100.
It is deterministic, so a user stays in or out of a rollout as long as the
percentage doesn't change.

Changing a flag's key moves every user to a new bucket. Don't rename flags that
are partially rolled out.

## Operators

`in` and `not_in` compare against a comma separated list. `contains` is a
substring check.
