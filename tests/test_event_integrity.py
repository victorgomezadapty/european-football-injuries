"""Small synthetic fixtures test edge conditions only; never enter analysis outputs."""
import unittest
import pandas as pd
from src.data.clean_data import clean_data
from src.data.validation import quality_flags
from src.features.burden import summarize_burden
from src.features.player_history import build_history, interval_union_days
from src.validation.leakage import assert_onset_features
from src.validation.temporal import assert_prior_dates


def make_raw(rows):
    base={'Season':'20/21','Injury':'Knee injury','Days':'5 days','Games missed':'2',
          'injury_from_parsed':'1/1/2021','injury_until_parsed':'1/5/2021',
          'player_name':'Test Player','player_age':'25','player_position':'Forward','club':'Test Club','league':'Test League'}
    return pd.DataFrame([{**base,**row} for row in rows],dtype='string')


def events(rows):
    df,_=clean_data(make_raw(rows))
    return build_history(df.loc[~df.exact_duplicate])


class EventIntegrity(unittest.TestCase):
    def test_inclusive_duration_preserves_source(self):
        df,_=clean_data(make_raw([{}]))
        self.assertEqual(df.loc[0,'Days'],'5 days')
        self.assertEqual(df.loc[0,'reported_days_out'],5)
        self.assertEqual(df.loc[0,'calculated_days_out'],4)
        self.assertEqual(df.loc[0,'duration_difference'],1)
        self.assertEqual(interval_union_days(df),5)

    def test_dates_are_us_and_invalid_dates_are_flagged(self):
        df,_=clean_data(make_raw([{'injury_from_parsed':'2/13/2021'}, {'injury_from_parsed':'31/12/2021'}]))
        self.assertEqual(df.loc[0,'injury_start'],pd.Timestamp('2021-02-13'))
        self.assertTrue(pd.isna(df.loc[1,'injury_start']))
        self.assertTrue(quality_flags(df,pd.Timestamp('2026-10-26')).loc[1,'injury_start_parse_failure'])

    def test_unparseable_and_negative_are_not_zero_filled(self):
        df,_=clean_data(make_raw([{'Days':'about 5 days','Games missed':'-'},{'Days':'-4 days'}]))
        self.assertTrue(df.days_out.isna().all())
        self.assertEqual(df.loc[1,'reported_days_out'],-4)
        self.assertTrue(pd.isna(summarize_burden(df,'league').loc[0,'total_days_out']))

    def test_exact_duplicate_exclusion_is_separate_from_context(self):
        df,_=clean_data(make_raw([{}, {}, {'club':'Loan Club'}]))
        self.assertEqual(df.exact_duplicate.tolist(),[False,True,False])
        self.assertTrue(df.potential_duplicate_episode.all())

    def test_same_day_records_are_not_prior_to_one_another(self):
        h=events([{}, {'Injury':'Ankle injury'}, {'injury_from_parsed':'1/9/2021','injury_until_parsed':'1/10/2021'}])
        self.assertEqual(h.previous_injury_count.tolist(),[0,0,2])
        self.assertTrue(pd.isna(h.loc[2,'days_since_previous_injury']))
        assert_prior_dates(h)

    def test_future_append_does_not_change_prior_counts(self):
        past=[{}, {'injury_from_parsed':'2/1/2021','injury_until_parsed':'2/5/2021'}]
        h=events(past)
        future=events(past+[{'injury_from_parsed':'3/1/2021','injury_until_parsed':'3/5/2021'}])
        self.assertEqual(h.previous_injury_count.tolist(),future.previous_injury_count.iloc[:2].tolist())
        self.assertEqual(h.previous_same_injury_count.tolist(),future.previous_same_injury_count.iloc[:2].tolist())

    def test_nested_intervals_detect_any_prior_overlap(self):
        h=events([{'injury_until_parsed':'1/31/2021','Days':'31 days'},
                  {'injury_from_parsed':'1/5/2021','injury_until_parsed':'1/8/2021','Days':'4 days'},
                  {'injury_from_parsed':'1/10/2021','injury_until_parsed':'1/12/2021','Days':'3 days'}])
        self.assertTrue(h.loc[2,'overlaps_any_prior_record'])
        self.assertEqual(h.loc[2,'days_since_previous_injury'],2)
        self.assertEqual(interval_union_days(h),31)

    def test_inclusive_shared_endpoint_is_overlap(self):
        h=events([{}, {'injury_from_parsed':'1/5/2021','injury_until_parsed':'1/8/2021','Days':'4 days'}])
        self.assertTrue(h.loc[1,'overlaps_any_prior_record'])
        self.assertEqual(h.loc[1,'same_label_after_recorded_end_count'],0)
        self.assertEqual(interval_union_days(h),8)

    def test_missing_end_does_not_imply_return(self):
        h=events([{'injury_until_parsed':''},{'injury_from_parsed':'2/1/2021','injury_until_parsed':'2/3/2021'}])
        self.assertTrue(pd.isna(h.loc[1,'days_since_previous_injury']))
        self.assertEqual(h.loc[1,'same_label_after_recorded_end_count'],0)

    def test_missing_names_and_labels_do_not_make_recurrence(self):
        h=events([{'player_name':''},{'Injury':''},{'Injury':'','injury_from_parsed':'2/1/2021'}])
        self.assertTrue(pd.isna(h.loc[0,'previous_injury_count']))
        self.assertTrue(h.loc[[1,2],'previous_same_injury_count'].isna().all())

    def test_leakage_guard_rejects_outcomes_and_full_history(self):
        for column in ['days_out','games_missed','career_injury_count_in_dataset','days_since_previous_injury']:
            with self.assertRaises(ValueError):
                assert_onset_features([column])


if __name__=='__main__':
    unittest.main()
