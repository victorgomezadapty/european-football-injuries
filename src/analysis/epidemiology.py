def frequencies(df, column):
    return df[column].value_counts(dropna=False).rename_axis(column).reset_index(name='record_count')
