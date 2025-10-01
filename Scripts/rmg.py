def rmg():
    import pandas as pd
    print ("Removing Goalkeepers...")
    ls = []
    df = pd.read_csv('ScrapeData/players_cleaned.csv')
    for index, row in df.iterrows():
        if row['Pos'] != 'GK':
            ls.append(row)
    pd.DataFrame(ls).to_csv('non_goalkeepers.csv', index=False)
    return df

rmg()
