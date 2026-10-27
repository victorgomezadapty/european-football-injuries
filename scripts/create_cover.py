"""Render an original branded chart cover from credited aggregate data."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
data=pd.read_csv(ROOT/'web/downloads/injury_burden.csv').nlargest(5,'total_days_out').iloc[::-1]
fig=plt.figure(figsize=(12,6),facecolor='#102e31')
fig.text(.055,.83,'FOOTBALL / RECORDED ABSENCE / 2020–2025',color='#c6f385',fontsize=10,fontfamily='monospace')
fig.text(.055,.61,'Football',color='#f6f5ef',fontsize=49,fontfamily='DejaVu Serif')
fig.text(.055,.44,'Injury Burden',color='#c6f385',fontsize=42,fontfamily='DejaVu Serif',style='italic')
fig.text(.06,.31,'15,603 records · 5 leagues',color='#d4e0d5',fontsize=15)
fig.text(.06,.23,'Analysis and visualization: Víctor Gómez',color='#b7cbbd',fontsize=10)
ax=fig.add_axes([.57,.25,.37,.46],facecolor='#102e31')
ax.barh(range(5),data.total_days_out,color=['#609785']*4+['#f78863'],height=.55)
ax.set_yticks(range(5),data.injury_type_raw,color='#e7efdf',fontsize=8)
ax.set_xticks([0,30000,60000],['0','30k','60k'],color='#adc5b5',fontsize=8)
ax.set_xlabel('Reported episode-days summed',color='#b7cbbd',fontsize=9)
ax.tick_params(length=0,pad=6)
for spine in ax.spines.values():spine.set_visible(False)
fig.text(.055,.07,'Source: Sanan Muzaffarov · European Football Injuries, Kaggle v2 · CC BY-SA 4.0',color='#9fbbac',fontsize=8)
fig.text(.055,.035,'Derived aggregate analysis. Counts are not incidence; episode sums can repeat days.',color='#9fbbac',fontsize=8)
fig.savefig(ROOT/'web/social.png',dpi=100,facecolor=fig.get_facecolor())
bundle=ROOT/'publication/kaggle';bundle.mkdir(parents=True,exist_ok=True)
fig.savefig(bundle/'dataset-cover-image.png',dpi=100,facecolor=fig.get_facecolor())
plt.close(fig)
print('Original aggregate chart cover created with source attribution.')
