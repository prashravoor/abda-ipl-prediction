from bs4 import BeautifulSoup
import requests

player_st_f = 'yaml/csv/bat_stats.csv'
bat_stats = {}
bat_stats['Pid'] = ['Pid', 'Name', 'Role', 'Mat', 'Inn', 'NO', 'Runs', 'HS',
                    'Avg', 'BF', 'SR', '100', '50', '4s', '6s']
try:
    with open(player_st_f, 'r') as pf:
        for l in pf.readlines():
            parts = l.split(',')
            parts = [x.strip() for x in parts if x.strip()]
            bat_stats[str(parts[0])] = parts
    pf.close()
except:
    print('No file exists, will be created')

player_st_f = 'yaml/csv/bowl_stats.csv'
bowl_stats = {}
bowl_stats['Pid'] = ['Pid', 'Name', 'Role', 'Mat', 'Inn', 'Balls', 'Runs', 'Wkts',
                    'BBI', 'BBM', 'Econ', 'Avg', 'SR', '5w', '10w']
try:
    with open(player_st_f, 'r') as pf:
        for l in pf.readlines():
            parts = l.split(',')
            parts = [x.strip() for x in parts if x.strip()]
            bowl_stats[str(parts[0])] = parts
    pf.close()
except:
    print('No file exists, will be created')

dummy_stats = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']

"""
names = []
with open('yaml/csv/names_list.csv') as f:
    for l in f.readlines():
        parts = l.split(',')
        names.extend(parts)
f.close()
"""

names_map  = {}
with open('yaml/csv/name_map.csv') as f:
    for l in f.readlines():
        parts = l.split(',')
        parts = [x.strip() for x in parts if x.strip()]
        names_map[parts[1]] = parts[0]
f.close()

mapper = {}
try:
    with open('yaml/csv/names_mapped.csv', 'r') as f:
        for l in f.readlines():
            parts = l.split(',')
            parts = [x.strip() for x in parts if x.strip()]
            mapper[parts[0]] = parts[1]
        f.close()
except:
    print('Mapped file doesnt exist, will be created')

names = names_map.keys()
failed_names = []

# Team IDs
for n in names:
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
        if p[1] == p1[1] and p[0][0] == p1[0][0]:
            pid = str(player['id'])
            break

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
    name = st.find('h1').text
    
    mapper[n] = name
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
    if len(ipl) == 0:
        row.extend(dummy_stats)
        bat_stats[pid] = row
        bowl_stats[pid] = row
        print('No stats found for player {}'.format(name))
        continue

    for i in ipl:
        r = i.find_all('td')
        try:
            float(r[6].text)
            r = r[1:]
            # Bat Stats
            for v in r:
                row.append(str(v.text))
            bat_stats[pid] = row
        except ValueError:
            # Bowl Stats
            # Remove IPL
            r = r[1:]
            for v in r:
                row.append(str(v.text))
            bowl_stats[pid] = row

player_st_f = 'yaml/csv/bat_stats.csv'
with open(player_st_f, 'w') as pf:
    for v in bat_stats.values():
        pf.write('{}\n'.format(','.join(v)))
    pf.close()

player_st_f = 'yaml/csv/bowl_stats.csv'
with open(player_st_f, 'w') as pf:
    for v in bowl_stats.values():
        pf.write('{}\n'.format(','.join(v)))
    pf.close()

with open('yaml/csv/names_mapped.csv', 'w') as f:
    for name, mapped in mapper.items():
        if name in names_map:
            f.write('{},{}\n'.format(names_map[name], mapped))
        else:
            f.write('{},{}\n'.format(name, mapped))
    for name in failed_names:
        f.write('{},{}\n'.format(name,name))
    f.close()

print('List of failed queries: {}'.format(failed_names))