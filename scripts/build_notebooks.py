"""Build and optionally execute the descriptive notebooks; deferred phases stay Markdown only."""
from pathlib import Path
import argparse
import json
import nbformat as nbf
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
SETUP='''from pathlib import Path
import sys
import json
import pandas as pd
from IPython.display import display, Image, Markdown
ROOT = Path.cwd()
if ROOT.name == 'notebooks':
    ROOT = ROOT.parent
if not (ROOT / 'reports/dataset_summary.json').exists():
    raise FileNotFoundError('Run python -m src.pipeline from the project root first.')
sys.path.insert(0, str(ROOT))
TABLES = ROOT / 'reports/tables'
def table(name):
    return pd.read_csv(TABLES / (name + '.csv'))
def figure(name):
    display(Image(filename=str(ROOT / 'reports/figures' / (name + '.png'))))
summary = json.loads((ROOT / 'reports/dataset_summary.json').read_text(encoding='utf-8'))
'''

NOTEBOOKS=[
('01_data_understanding','Data understanding',
 'Verify the source dimensions, exact headers, dates and data quality before interpretation.',[
 'display(summary)\ndisplay(table("data_dictionary"))',
 'display(table("missingness"))\ndisplay(table("quality_summary"))',
 'display(table("duration_comparison"))\ndisplay(table("duplicate_sensitivity"))',
 'display(table("potential_duplicate_episodes")[["player_name", "club", "season", "injury_type_raw", "injury_start", "injury_end"]].head(20))'],
 'One record is an injury or other recorded absence with club/season context. Candidate repeated episodes and inclusive durations are material interpretation issues.'),
('02_injury_epidemiology','Recorded injury and absence frequency',
 'Which labels and player contexts have the most recorded events? These are frequencies without exposure denominators.',[
 'from src.analysis.epidemiology import frequencies\nfrom src.data.load_data import load_raw\nraw, manifest = load_raw(ROOT)\ndisplay(frequencies(raw, "Injury").head(20))',
 'display(table("distribution_position"))\ndisplay(table("distribution_league"))\ndisplay(table("distribution_season"))',
 'display(table("distribution_age_recorded"))\ndisplay(table("distribution_club"))',
 'figure("top_injury_frequency")\nfigure("position_injury_mix")'],
 'Do not interpret more records as higher individual risk. Healthy squads and match/training exposure are missing.'),
('03_injury_severity','Continuous duration and games missed',
 'How long are recorded absences? Analyze continuous values and report support before ranking rare labels.',[
 'display(table("numeric_distributions"))\ndisplay(table("duration_comparison"))',
 'severity=table("injury_ranking_median_days_out")\ndisplay(severity.head(15))\ndisplay(severity.loc[severity.valid_days_count >= 20].head(15))',
 'figure("time_loss_distributions")\nfigure("age_duration")'],
 'Reported durations use inclusive dates. No arbitrary severe-injury category is created. Recorded age timing is uncertain and age summaries are unadjusted/event-weighted.'),
('04_injury_burden','Frequency, severity and burden',
 'Which recorded labels account for the greatest episode-day and match-loss totals?',[
 'display(table("injury_ranking_total_days_out").head(15))\ndisplay(table("injury_ranking_total_games_missed").head(15))',
 'display(table("burden_by_position"))\ndisplay(table("burden_by_league"))\ndisplay(table("burden_by_season"))',
 'display(table("duplicate_sensitivity"))\nfigure("injury_burden_matrix")',
 'figure("top_time_loss_burden")\nfigure("top_match_loss_burden")'],
 'Episode sums can double count repeated/overlapping intervals. Candidate collapsing is sensitivity, not adjudicated club attribution or verified independent injuries.'),
('05_player_injury_history','Player histories and recorded intervals',
 'How heterogeneous are named player histories and where do recorded intervals overlap?',[
 'profiles=table("player_burden_profiles")\ndisplay(profiles.head(15))\ndisplay(table("injuries_per_player_distribution"))',
 'display(table("example_player_timelines")[["player_name","injury_type_raw","injury_start","injury_end","previous_injury_count","days_since_previous_injury"]])',
 'figure("player_injury_timelines")'],
 'Name surrogates are not verified player IDs. Full-history profiles are descriptive only. Gaps do not establish healthy or eligible time.'),
('06_recurrence_patterns','Repeated recorded labels',
 'How often do later starts repeat a label, and how does candidate collapsing affect this description?',[
 'display(table("recurrence_by_label").head(20))\ndisplay(table("recurrence_candidate_sensitivity").head(20))',
 'display(table("inter_record_gap_distribution"))\ndisplay(table("inter_record_gaps").head(20))',
 'display(table("injury_taxonomy_draft").head(25))\ndisplay(table("label_normalization_variants"))'],
 'Same-label repetition is not clinical reinjury. Anatomical-region recurrence is deferred until the taxonomy is approved; prior end-date gaps are retrospective and may overlap.'),
('07_time_loss_survival','Time-to-return analysis — deferred',None,[],
 'Milestone 1 review is required before survival analysis. First verify endpoint meaning, actual vs expected return, observation cutoffs, censoring and repeated-player dependence. No curves or models are fitted here.'),
('08_seasonal_patterns','Season and calendar distributions',
 'When are onsets recorded and how does the source season context differ from calendar timing?',[
 'display(table("burden_by_season"))\ndisplay(table("burden_by_league_season"))',
 'display(table("calendar_month_burden"))\nfigure("monthly_recorded_events")'],
 'Burden is assigned wholly to source season/onset month rather than apportioned across calendar days. Recording coverage and activity differ; schedule causes are not established.'),
('09_player_availability_profiles','Recorded Availability Burden Profiles',
 'What can the file summarize about recorded absence consequences without an availability denominator?',[
 'display(table("player_burden_profiles")[["player_name","career_injury_count_in_dataset","total_days_out","total_games_missed","median_days_out","max_days_out","recorded_interval_union_days"]].head(20))',
 'display(Markdown((ROOT / "docs/availability_definition.md").read_text(encoding="utf-8")))\ndisplay(table("duplicate_sensitivity"))'],
 'No availability percentage is computed. Eligible fixtures, squad/registration intervals, verified exposure and observation windows are absent.'),
('10_future_data_integration','Future integration — deferred',None,[],
 'External data integration is deferred until Milestone 1 review. Proposed order: verified player IDs; transfer/registration intervals; fixture eligibility; match/training exposure; endpoint verification. No external rows are acquired or joined here.'),
]


def build(execute=False):
    folder=ROOT/'notebooks'
    folder.mkdir(exist_ok=True)
    for slug,title,question,codes,interpretation in NOTEBOOKS:
        cells=[nbf.v4.new_markdown_cell('# '+title+'\n\n'+(question or 'Reserved for Phase 2.'))]
        if codes:
            cells.append(nbf.v4.new_code_cell(SETUP))
            cells += [nbf.v4.new_code_cell(code) for code in codes]
        cells.append(nbf.v4.new_markdown_cell('## Interpretation and limits\n\n'+interpretation))
        notebook=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}})
        if execute and codes:
            NotebookClient(notebook,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
        nbf.validate(notebook)
        path=folder/(slug+'.ipynb')
        nbf.write(notebook,path)
        print(f'{slug}: '+('executed' if execute and codes else 'deferred' if not codes else 'built'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute',action='store_true')
    build(parser.parse_args().execute)
