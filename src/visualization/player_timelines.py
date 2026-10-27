import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from .injury_plots import save,TEAL,NAVY


def plot_timelines(events,profiles,directory):
    selected=profiles.sort_values(['career_injury_count_in_dataset','player_name'],ascending=[False,True]).head(3)
    fig,axes=plt.subplots(len(selected),1,figsize=(13,8),layout='constrained',squeeze=False)
    for ax,player in zip(axes.flat,selected.itertuples()):
        p=events[events.player_id.eq(player.player_id) & events.calculated_days_out.ge(0)].sort_values('injury_start')
        for lane,row in enumerate(p.itertuples()):
            start=mdates.date2num(row.injury_start)
            width=(row.injury_end-row.injury_start).days+1
            ax.broken_barh([(start,width)],(lane-.35,.7),facecolors=TEAL)
        ax.set_yticks(range(len(p)),[str(x) for x in p.injury_type_raw],fontsize=7)
        ax.set_title(str(player.player_name)+' | descriptive example selected by record count',loc='left',fontsize=10)
        ax.xaxis_date()
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.grid(axis='x',alpha=.2)
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Recorded player histories: each bar is one source record',color=NAVY)
    fig.text(.01,-.025,'Intervals use inclusive date endpoints. Gaps indicate no recorded absence; they do not establish health or eligibility.',fontsize=9)
    save(fig,directory,'player_injury_timelines')
    return events[events.player_id.isin(selected.player_id)].sort_values(['player_name','injury_start','source_row'])
