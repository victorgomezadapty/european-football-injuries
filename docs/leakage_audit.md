# Future leakage audit — no model trained

| Variable | Timing concern | Current use |
| --- | --- | --- |
| Days / calculated duration | Outcome known at recorded end | Descriptive outcome only |
| Games missed | Accumulates after injury onset | Descriptive outcome only |
| Injury end | Post-onset endpoint | Retrospective sequences/interval unions |
| Full-history record counts and burden | Includes future records at earlier dates | Descriptive player profiles only |
| Future repeated-label events | Requires subsequent records | Retrospective recurrence only |
| Previous counts | Computed from starts strictly before current date | Potential feature, pending publication/recording-time audit |
| Previous end / gap | Earlier injury may still be ongoing; end then future-known | Retrospective; excluded by onset guard |
| Same-label-after-recorded-end count | Uses prior outcomes and source endpoint interpretation | Retrospective; excluded by onset guard |
| Age, position, club, league | May describe collection/season context rather than onset | Must verify effective dates before modeling |
| Injury diagnosis label | Final diagnosis may differ from information at onset | Audit intended prediction time |
| Season | Calendar known but coverage and source context differ | Audit attribution |

Same-day starts are ties and cannot be used as earlier history for one another. Adding future records must not alter previously computed prior start counts. Undated prior records cannot be ordered and are excluded from chronological counts. The guard in `src/validation/leakage.py` rejects listed post-onset/full-history fields, but passing it does not certify feature availability. No train/test split or prediction is performed.

Any later recovery model needs an explicit prediction time, source knowledge timestamps, chronological evaluation, repeated-player handling and an audit of outcome availability. A severe-injury target defined by days must never include days or future games missed as onset predictors.
