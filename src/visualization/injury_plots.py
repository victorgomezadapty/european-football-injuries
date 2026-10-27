from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TEAL='#087f8c'
NAVY='#18364c'
ORANGE='#d77732'


def save(fig, directory, name):
    directory=Path(directory)
    directory.mkdir(parents=True,exist_ok=True)
    fig.savefig(directory / f'{name}.png',dpi=180,bbox_inches='tight',facecolor='white')
    fig.savefig(directory / f'{name}.svg',bbox_inches='tight',facecolor='white')
    plt.close(fig)


def bar_chart(table, key, metric, title, xlabel, directory, filename):
    selected=table.sort_values(metric,ascending=False).head(12).iloc[::-1]
    fig,ax=plt.subplots(figsize=(10,6),layout='constrained')
    ax.barh(selected[key].fillna('Missing').astype(str),selected[metric].astype(float),color=TEAL)
    ax.set(title=title,xlabel=xlabel)
    ax.spines[['top','right']].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis='x',alpha=.18)
    fig.text(.01,-.035,'Recorded absence events. Counts and episode sums have no exposure denominator.',fontsize=9,color=NAVY)
    save(fig,directory,filename)


def burden_matrix(table,directory):
    t=table.dropna(subset=['median_days_out','total_games_missed']).copy()
    fig,ax=plt.subplots(figsize=(12,8),layout='constrained')
    maxgames=t.total_games_missed.max()
    areas=15+1000*t.total_games_missed.astype(float)/maxgames if maxgames else np.repeat(15,len(t))
    ax.scatter(t.injury_count,t.median_days_out,s=areas,c=TEAL,alpha=.55,edgecolors='white',linewidth=.6)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set(xlabel='Recorded events (log scale)',ylabel='Median reported days out (log scale)',title='Injury burden matrix: frequency, duration and missed matches')
    # Label a small set close to their bubbles; keep labels distinct from the legend.
    selected=t.nlargest(5,'total_days_out')
    offsets=[(16,10),(-145,12),(-90,30),(-120,-22),(-155,-5)]
    for offset,(_,row) in enumerate(selected.iterrows()):
        ax.annotate(str(row.injury_type_raw),xy=(row.injury_count,row.median_days_out),
            xytext=offsets[offset],textcoords='offset points',fontsize=9,
            arrowprops={'arrowstyle':'-','color':NAVY,'alpha':.45})
    ax.axvline(t.injury_count.median(),color=NAVY,ls=':',lw=1)
    ax.axhline(t.median_days_out.median(),color=NAVY,ls=':',lw=1)
    ax.grid(alpha=.12)
    legend=[]
    for value in [100,1000,5000]:
        legend.append(ax.scatter([],[],s=15+1000*value/maxgames,color=TEAL,alpha=.55,label=f'{value:,} games'))
    ax.legend(handles=legend,title='Bubble area: games missed',loc='upper right',labelspacing=1.3)
    fig.text(.01,-.045,'All raw labels retained. Reference lines are medians across labels, not clinical cutoffs. Potential duplicate episodes retained.',fontsize=9)
    save(fig,directory,'injury_burden_matrix')


def distributions(events,directory):
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
    for ax,col,label in zip(axes,['days_out','games_missed_valid'],['Reported days out','Reported games missed']):
        values=events[col].dropna().astype(float)
        bins=np.geomspace(1,max(2,values.max()+1),40)
        ax.hist(values,bins=bins,color=TEAL,edgecolor='white',linewidth=.4)
        ax.set_xscale('log')
        ax.set(xlabel=label+' (log scale)',ylabel='Recorded events')
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Time loss and match loss have long right tails')
    save(fig,directory,'time_loss_distributions')


def temporal_plot(table,directory):
    t=table[table.injury_month.notna()].sort_values('injury_month')
    fig,ax=plt.subplots(figsize=(12,4.5),layout='constrained')
    ax.plot(t.injury_month.astype(str),t.injury_count,color=TEAL,lw=1.8)
    ax.set(xlabel='Month of recorded onset',ylabel='Recorded events',title='Calendar distribution of recorded absence onsets')
    ticks=np.arange(0,len(t),6)
    ax.set_xticks(ticks,t.injury_month.iloc[ticks].astype(str),rotation=40,ha='right')
    ax.spines[['top','right']].set_visible(False)
    fig.text(.01,-.04,'Counts reflect recording and coverage as well as football activity. No exposure adjustment.',fontsize=9)
    save(fig,directory,'monthly_recorded_events')


def position_heatmap(events,directory):
    top=events.injury_type_raw.value_counts().head(10).index
    t=events[events.injury_type_raw.isin(top)].groupby(['position','injury_type_raw']).size().unstack(fill_value=0).reindex(columns=top)
    fig,ax=plt.subplots(figsize=(12,7),layout='constrained')
    im=ax.imshow(t.values,cmap='Blues',aspect='auto')
    ax.set_xticks(range(len(t.columns)),t.columns,rotation=40,ha='right')
    ax.set_yticks(range(len(t.index)),t.index)
    ax.set_title('Recorded injury mix by detailed position: ten most frequent labels')
    fig.colorbar(im,ax=ax,label='Recorded events',shrink=.8)
    for y in range(len(t)):
        for x in range(len(t.columns)):
            ax.text(x,y,str(t.iloc[y,x]),ha='center',va='center',fontsize=8,color='white' if t.iloc[y,x]>t.values.max()*.55 else NAVY)
    save(fig,directory,'position_injury_mix')


def age_plot(events,directory):
    fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
    t=events.groupby('age_recorded',dropna=True).days_out.agg(['median','count',lambda s:s.quantile(.25),lambda s:s.quantile(.75)])
    t.columns=['median','n','p25','p75']
    ax.fill_between(t.index.astype(float),t.p25.astype(float),t.p75.astype(float),color=TEAL,alpha=.2,label='Event IQR')
    ax.plot(t.index.astype(float),t['median'].astype(float),color=TEAL,label='Event median')
    ax.set(xlabel='Recorded age (years)',ylabel='Reported days out',title='Duration by recorded age: descriptive, unadjusted association')
    ax.legend()
    fig.text(.01,-.04,'Age timing is not independently verified. Injury mix, repeated players and sample sizes may differ.',fontsize=9)
    save(fig,directory,'age_duration')
