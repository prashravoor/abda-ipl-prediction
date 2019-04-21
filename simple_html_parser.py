from bs4 import BeautifulSoup
import requests


def load_names(deliveries_file, teams_file):
    names = set()
    with open(deliveries_file) as file:
        for line in file.readlines():
            names.add(line.split(",")[2])
            names.add(line.split(",")[3])
    file.close()

    # Some names don't have a proper conversion
    name_map = {}

    remove_names = ['DJ Bravo', 'DM Bravo', 'RG Sharma',
                    'R Sharma', 'BAW Mendis', 'BMAJ Mendis', 'J Theron']
    for x in remove_names:
        names.remove(x)

    # print(len(names))

    for name in names:
        parts = name.split()
        if parts[0].isupper():
            name_map[str(parts[0][0]) + ' ' + ' '.join(parts[1:])] = name
        else:
            name_map[name] = name
    
    name_map['Dwayne Bravo'] =  'DJ Bravo'
    name_map['Darren Bravo'] = 'DM Bravo'
    name_map['Rohit Sharma'] = 'RG Sharma'
    name_map['Rahul Sharma'] = 'R Sharma'
    name_map['Tharindu Mendis'] = 'BAW Mendis' 
    name_map['Jeevan Mendis'] = 'BMAJ Mendis'
    name_map['Rusty Theron'] = 'J Theron'
    name_map['KL Rahul'] = 'K Rahul'
    name_map['F Maharoof'] = 'M Maharoof'
    name_map['M Jayawardane'] = 'DPMD Jayawardene'
    name_map['A Morkel'] = 'JA Morkel'
    name_map['Chamara Silva'] = 'LPC Silva'
    name_map['Gnaneswara Rao'] = 'Y Gnaneswara Rao'
    name_map['D Mascarenhas'] = 'AD Mascarenhas'
    name_map['L Malinga'] = 'SL Malinga'

    with open(teams_file, 'r') as file:
        for l in file.readlines():
            parts = [x.strip() for x in l.split(',') if x.strip()]
            for part in parts:
                # Retain same names on LHS and RHS
                name_map[part] = part

    return name_map


def get_all_player_stats(deliveries_file='data/all_deliveries.csv', teams_file='data/teams.csv',
                         bat_st_f='data/bat_stats.csv', bowl_st_f='data/bowl_stats.csv', 
                         namefile='data/names_mapped.csv'):
    # bat_st_f = 'yaml/csv/bat_stats.csv'
    bat_stats = {}
    # bat_stats['Pid'] = ['Pid', 'Name', 'Role', 'Mat', 'Inn', 'NO', 'Runs', 'HS',
    #                    'Avg', 'BF', 'SR', '100', '50', '4s', '6s']
    try:
        pf = open(bat_st_f, 'r')
        for l in pf.readlines():
            parts = l.split(',')
            parts = [x.strip() for x in parts if x.strip()]
            bat_stats[str(parts[0])] = parts
        pf.close()
    except:
        print('No file exists for Batting Stats, will be created')
        pf = open(bat_st_f, 'w')
        pf.write('{}\n'.format(','
                               .join(['Pid', 'Name', 'Role', 'Mat', 'Inn', 'NO', 'Runs', 'HS',
                                      'Avg', 'BF', 'SR', '100', '200', '50', '4s', '6s'])))
        pf.close()

    # bowl_st_f = 'yaml/csv/bowl_stats.csv'
    bowl_stats = {}
    # bowl_stats['Pid'] = ['Pid', 'Name', 'Role', 'Mat', 'Inn', 'Balls', 'Runs', 'Wkts',
    #                    'BBI', 'BBM', 'Econ', 'Avg', 'SR', '5w', '10w']
    try:
        pf = open(bowl_st_f, 'r')
        for l in pf.readlines():
            parts = l.split(',')
            parts = [x.strip() for x in parts if x.strip()]
            bowl_stats[str(parts[0])] = parts
        pf.close()
    except:
        print('No file exists for Bowling Stats, will be created')
        pf = open(bowl_st_f, 'w')
        pf.write('{}\n'.format(','.join(['Pid', 'Name', 'Role', 'Mat', 'Inn', 'Balls', 'Runs', 'Wkts',
                                         'BBI', 'BBM', 'Econ', 'Avg', 'SR', '5w', '10w'])))
        pf.close()

    names_map = load_names(deliveries_file, teams_file)
    print('Will fetch statistics for {} names'.format(len(names_map)))
    
    # namefile = 'yaml/csv/names_mapped.csv'
    mapper = {}
    try:
        with open(namefile, 'r') as f:
            for l in f.readlines():
                parts = l.split(',')
                parts = [x.strip() for x in parts if x.strip()]
                mapper[parts[0]] = parts[1]
            f.close()
    except:
        print('Names Mapped file doesnt exist, will be created')
        open(namefile, 'w').close()

    batf = open(bat_st_f, 'a')
    bowlf = open(bowl_st_f, 'a')
    name_mapped_f = open(namefile, 'a')

    dummy_stats = ['0', '0', '0', '0', '0',
                   '0', '0', '0', '0', '0', '0', '0', '0']

    names = names_map.keys()
    failed_names = []
    # cnt = 0
    # Team IDs
    for n in names:
        # if cnt >= 5:
        #    break
        # cnt += 1
        if names_map[n] in mapper or n in mapper.values():
            print('Player {} already found, skipping'.format(n))
            continue

        row = []
        url = 'https://www.cricbuzz.com/api/search/results'
        res = requests.get(url, params={'q': n}).json()
        if not res or 'playerList' not in res or len(res['playerList']) == 0:
            print('Failed to get valid response for player {}, Skipping'.format(n))
            failed_names.append(n)
            continue
        pid = ''
        for player in res['playerList']:
            p = [x.lower() for x in player['title'].split()]
            p1 = [x.lower() for x in n.split()]
            try:
                if (p[1] == p1[1] and p[0][0] == p1[0][0]):
                    pid = str(player['id'])
                    break
            except Exception as e:
                print(e)
                if len(p) == 1:
                    if p == p1:
                        pid = str(player['id'])
                    else:
                        print('Failed to get stats for Player {}, {}'.format(n, e))

        if not pid:
            print('Failed to get valid player Id for {}!'.format(n))
            failed_names.append(n)
            continue

        if pid in bat_stats or pid in bowl_stats:
            print('Player {} already exists, skipping'.format(pid))
            continue

        # print('Getting stats for player {}, {}'.format(name, pid))

        player_stats_url = 'https://www.cricbuzz.com/profiles/{}'.format(pid)
        stats_text = requests.get(player_stats_url).text
        st = BeautifulSoup(stats_text, features='html5lib')
        name = st.find('h1')
        if not name:
            continue
        name = name.text
        mapper[names_map[n]] = name
        #if n in names_map:
        #    name_mapped_f.write('{},{}\n'.format(n, name))
        #else:
        name_mapped_f.write('{},{}\n'.format(names_map[n], name))

        row.append(str(pid))
        row.append(str(name))
        j = 0
        divs = st.find_all('div')
        for x in divs:
            if x.text == 'Role':
                break
            j += 1
        role = divs[j+1].text.strip()
        row.append(str(role))

        print('Writing stats for player {}, {}, Role: {}'.format(name, pid, role))
        ipl = [x for x in st.find_all('tr') if 'IPL' in x.text]

        bat_row_added = False
        bowl_row_added = False
        for i in ipl:
            bat_row = list(row)
            bowl_row = list(row)
            r = i.find_all('td')
            try:
                float(r[6].text)
                r = r[1:]
                # Bat Stats
                for v in r:
                    bat_row.append(str(v.text))
                bat_stats[pid] = bat_row
                batf.write('{}\n'.format(','.join(bat_row)))
                bat_row_added = True
            except ValueError:
                # Bowl Stats
                # Remove IPL
                r = r[1:]
                for v in r:
                    if v.text == '-':
                        bowl_row.append('0')
                    else:
                        bowl_row.append(str(v.text))
                bowl_stats[pid] = bowl_row
                bowlf.write('{}\n'.format(','.join(bowl_row)))
                bowl_row_added = True

        if not bat_row_added:
            bat_row = list(row)
            bat_row.extend(dummy_stats)
            bat_stats[pid] = bat_row
            batf.write('{}\n'.format(','.join(bat_row)))
            print('No Bat stats found for player {}'.format(name))

        if not bowl_row_added:
            bowl_row = list(row)
            bowl_row.extend(dummy_stats[:-1])
            bowl_stats[pid] = bowl_row
            bowlf.write('{}\n'.format(','.join(bowl_row)))
            print('No Bowl stats found for player {}'.format(name))

    print('List of failed queries: {}'.format(failed_names))
    #for name in failed_names:
    #    name_mapped_f.write('{},{}\n'.format(name, name))

    batf.close()
    bowlf.close()
    name_mapped_f.close()


if '__main__' == __name__:
    get_all_player_stats()