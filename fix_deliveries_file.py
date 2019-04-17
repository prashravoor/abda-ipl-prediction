import pandas as pd

def make_clusters(deliveries_file='data/all_deliveries_names_fixed.csv',
                  bat_clusters='data/bat_clusters.csv', bowl_clusters='data/bowl_clusters.csv',
                  out_file='data/cluster_deliveries.csv'):
    df = pd.read_csv(deliveries_file)
    names_map_bat = pd.DataFrame()
    names_map_bat['Name'] = df.Batsman

    bat_clusters = pd.read_csv(bat_clusters)
    bat_table = bat_clusters.loc[:, ['Name', 'Cluster']]
    bat_joined = names_map_bat.merge(
        right=bat_table, how='inner', on='Name').drop_duplicates()

    names_map_bowl = pd.DataFrame()
    names_map_bowl['Name'] = df.Bowler

    bowl_clusters = pd.read_csv(bowl_clusters)
    bowl_table = bowl_clusters.loc[:, ['Name', 'Cluster']]
    bowl_joined = names_map_bowl.merge(
        right=bowl_table, how='inner', on='Name').drop_duplicates()

    new_batsman = []
    for b in df.Batsman:
        c = bat_joined.loc[bat_joined.Name == b, 'Cluster']
        if c.shape[0] == 0:
            # print('No Cluster found for batsman {}! Assigning default cluster'.format(b))
            new_batsman.append(0)
        else:
            new_batsman.append(c.iloc[0])

    new_bowler = []
    for b in df.Bowler:
        c = bowl_joined.loc[bowl_joined.Name == b, 'Cluster']
        if c.shape[0] == 0:
            # print('No cluster found for bowler {}! Assigning default cluster'.format(b))
            new_bowler.append(0)
        else:
            new_bowler.append(c.iloc[0])

    df = df.drop('Batsman', axis=1).drop('Bowler', axis=1)
    df['Batsman'] = new_batsman
    df['Bowler'] = new_bowler

    df.to_csv(out_file, index=False, header=True)


def fix_deliveries_data(deliveries_file='data/all_deliveries.csv', names_file='data/names_mapped.csv',
                        deliveries_out_file='data/all_deliveries_names_fixed.csv'):
    df = pd.read_csv(deliveries_file)
    name_map = {}

    """
    name_map['DJ Bravo'] = 'Dwayne Bravo'
    name_map['DM Bravo'] = 'Darren Bravo'
    name_map['RG Sharma'] = 'Rohit Sharma'
    name_map['R Sharma'] = 'Rahul Sharma'
    name_map['BAW Mendis'] = 'Tharindu Mendis'
    name_map['BMAJ Mendis'] = 'Jeevan Mendis'
    """
    with open(names_file) as f:
        for line in f.readlines():
            parts = [x.strip() for x in line.split(',') if x and x.strip()]
            if len(parts) > 0:
                name_map[parts[0]] = parts[1]
        f.close()

    for name, value in name_map.items():
        df = df.replace(name, value)

    df.Innings = df.Innings.astype(str).replace('1st innings', '1')
    df.Innings = df.Innings.astype(str).replace('2nd innings', '2')

    inns = []
    for i in df.Innings:
        if 'Super Over' in i:
            inns = '3'
        else:
            inns = i

    df.Innings = inns
    df.to_csv(deliveries_out_file, index=False, header=True)


if __name__ == '__main__':
    fix_deliveries_data()
    make_clusters()
