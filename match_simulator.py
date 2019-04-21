import random
import predict
import pandas as pd


class Player:
    def __init__(self, name, is_batsman, is_bowler):
        self.name = name
        self.is_batsman = is_batsman
        self.is_bowler = is_bowler

    def __str__(self):
        return self.name


class Bowler(Player):
    def __init__(self, name):
        Player.__init__(self, name, False, True)
        self.wickets = 0
        self.runs = 0
        self.extras = 0
        self.overs_bowled = 0
        self.num_deliveries = 0
        self.wicket_types = []

    def __update_deliveries(self):
        self.num_deliveries += 1

        if self.num_deliveries == 6:
            self.overs_bowled += 1
            self.num_deliveries = 0

    def runs_conceded(self, runs):
        self.runs += runs
        self.__update_deliveries()

    def extras_conceded(self, extras, extra_ball=False):
        self.extras += extras
        if extra_ball:
            self.num_deliveries -= 1
        self.__update_deliveries()

    def wicket_taken(self, wicket_type):
        if wicket_type not in ['run out']:
            self.wickets += 1
            self.wicket_types.append(wicket_type)
        self.__update_deliveries()

    def figures(self):
        return '{} / {} ({}.{})'.format(self.wickets, self.runs + self.extras, self.overs_bowled, self.num_deliveries)


class Batsman(Player):
    def __init__(self, name):
        Player.__init__(self, name, True, False)
        self.playing = False
        self.out = False
        self.runs = 0
        self.num_deliveries = 0
        self.fours = 0
        self.sixes = 0
        self.out_type = ""

    def start_play(self):
        self.playing = True

    def runs_scored(self, runs):
        self.runs += runs
        self.num_deliveries += 1
        if runs == 4:
            self.fours += 1
        elif runs == 6:
            self.sixes += 1

    def got_out(self, out_type):
        self.num_deliveries += 1
        self.playing = False
        self.out = True
        self.out_type = out_type

    def is_playing(self):
        return self.playing

    def figures(self):
        if self.out:
            return '{} ({})'.format(self.runs, self.num_deliveries)
        return '{}* ({})'.format(self.runs, self.num_deliveries)


class AllRounder(Batsman, Bowler):
    def __init__(self, name):
        Batsman.__init__(self, name)
        Bowler.__init__(self, name)
        Player.__init__(self, name, True, True)
    
    def a_figures(self):
        return Bowler.figures(self)

class Team:
    def __init__(self, name, members):
        self.name = name
        self.members = members

    def get_bowlers(self):
        bowlers = []
        for player in self.members:
            if player.is_bowler:
                bowlers.append(player)

        return bowlers


class Innings:
    def __init__(self, batting_team, bowling_team):
        self.score = 0
        self.wickets = 0
        self.extras = 0
        self.deliveries = 0
        self.striker = None
        self.non_striker = None
        self.bowler = None
        self.bowlers = {}
        # Role redressal - all batting team are batsmen
        batting_team_members = [Batsman(x.name) for x in batting_team.members]
        bowling_team_members = bowling_team.members
        self.batting_team = Team(batting_team.name, batting_team_members)
        self.bowling_team = Team(bowling_team.name, bowling_team_members)

    def stop_innings(self):
        if self.wickets == 10 or self.deliveries == 120:
            return True
        return False

    def runs_scored(self, runs):
        self.score += runs
        self.deliveries += 1
        self.striker.runs_scored(runs)
        self.bowler.runs_conceded(runs)
        if (runs % 2 != 0):  # Rotate strike
            self.striker, self.non_striker = self.non_striker, self.striker

    def extras_conceded(self, extras, extra_ball=False):
        self.score += extras
        self.extras += extras
        self.bowler.extras_conceded(extras, extra_ball)
        if not extra_ball:
            self.deliveries += 1
            self.striker.num_deliveries += 1

    def over_up(self, new_bowler):
        if not new_bowler in self.bowlers:
            self.bowlers[new_bowler] = 0
        self.bowlers[self.bowler] += 1
        self.bowler = new_bowler
        self.striker, self.non_striker = self.non_striker, self.striker

    def wicket(self, wicket_type, batsman, striker=True, crossover=False):
        b = None
        self.wickets += 1
        self.deliveries += 1
        self.bowler.wicket_taken(wicket_type)
        if striker:
            self.striker.got_out(wicket_type)
            b = self.striker
            self.striker = batsman
        else:
            self.non_striker.got_out(wicket_type)
            b = self.non_striker
            self.non_striker = batsman
        if crossover:
            self.striker, self.non_striker = self.non_striker, self.striker
        if batsman:
            batsman.start_play()
        return b

    def start_innings(self, bowler):
        self.bowler = bowler
        self.bowlers[bowler] = 0
        self.striker = self.batting_team.members[0]
        self.non_striker = self.batting_team.members[1]
        self.striker.start_play()

    def display(self):
        print(self.batting_team.name)
        for player in self.batting_team.members:
            detail = player.name
            if player.out:
                detail += '{}\t'.format(player.out_type)
            else:
                detail += '\t'
            detail += '{} ({})'.format(player.runs, player.num_deliveries)
            if player.is_playing():
                detail += '*'
            print(detail)
        print('Extras: {}\nTotal Score: {} - {}'.format(self.extras,
                                                        self.score, self.wickets))
        print('Bowling Team: {}'.format(self.bowling_team.name))
        for bowler in self.bowlers:
            detail = bowler.name
            if bowler.is_batsman:
                detail += ' ' + bowler.a_figures()
            else:
                detail += ' ' + bowler.figures()
            print(detail)

        print('Overs: {}.{}'.format(int(self.deliveries/6), self.deliveries % 6))


class Match:
    def __init__(self, first_bat, chaser):
        self.first_innings = Innings(first_bat, chaser)
        self.second_innings = Innings(chaser, first_bat)
        self.current_inns = None
        self.inn_num = 0

    def start_match(self):
        bowler = select_bowler(
            self.first_innings.bowling_team, 1, None, self.first_innings.bowlers, 0)
        self.first_innings.start_innings(bowler)
        self.current_inns = self.first_innings
        print('Starting the Match! Team Batting First: {}, First Bowler: {}'.format(
            self.current_inns.batting_team.name, bowler.name))
        self.inn_num = 1

    def start_chase(self):
        bowler = select_bowler(
            self.second_innings.bowling_team, 2, None, self.second_innings.bowlers, 0)
        self.second_innings.start_innings(bowler)
        self.current_inns = self.second_innings
        print('Starting the Chase! First Bowler: {}'.format(bowler.name))
        self.inn_num = 2

    def conduct_delivery(self, over, ball_num):
        ball_counts = True
        global bowl_clusters
        global bat_clusters
        # Attributes are of the form: ['Delivery', 'Innings', 'Batsman', 'Bowler', 'BowlerOver', 'Wickets', 'TeamScore']
        d_id = float('{}.{}'.format(over, ball_num))
        delivery = [d_id,
                    self.inn_num,
                    bat_clusters[self.current_inns.striker.name],
                    bowl_clusters[self.current_inns.bowler.name],
                    self.current_inns.bowlers[self.current_inns.bowler] + 1,
                    self.current_inns.wickets, self.current_inns.score]
        event = predict.predict_delivery(delivery, 'Result')
        if event == 'Wicket':
            crossover = False
            striker = True
            wicket_type = predict.predict_delivery(delivery, 'Wicket')
            if wicket_type in ['caught', 'run out']:
                striker = (random.random() < 0.5)
                crossover = (random.random() < 0.5)

            new_batsman = select_batsman(self.current_inns.batting_team,
                                         self.current_inns.striker,
                                         self.current_inns.non_striker, striker)
            batsman = self.current_inns.wicket(
                wicket_type, new_batsman, striker, crossover)
            print('Wicket Falls! Out Batsman: {}, Bowler: {}, Crossover: {}, New Batsman: {}'.format(
                batsman.name,
                self.current_inns.bowler.name,
                crossover,
                new_batsman))
            print('Batsman Figures: {}'.format(batsman.figures()))
        elif event == 'Extras':
            extra_ball = False
            extra_type = predict.predict_delivery(delivery, 'ExtraType')
            extra_runs = predict.predict_delivery(delivery, 'Extras')[0]
            if extra_type in ['wides', 'noballs']:
                extra_ball = True
                ball_counts = False
            self.current_inns.extras_conceded(extra_runs, extra_ball)
            print('Extras! Bowler: {}, Extra Type: {}, Runs: {}'.format(
                self.current_inns.bowler.name,
                extra_type,
                extra_runs))
        else:
            num_runs = predict.predict_delivery(delivery, 'Runs')
            print('Runs Scored. Batsman: {}, Bowler: {}, Num Runs: {}'.format(self.current_inns.striker.name,
                                                                              self.current_inns.bowler.name, num_runs))
            self.current_inns.runs_scored(num_runs)
        print('Current Innings Score: {}'.format(self.current_inns.score))
        return ball_counts

    def conduct_first_innings(self):
        deliveries = 0
        cur_ball_num = 0
        over = 0
        while not self.current_inns.stop_innings():
            if deliveries == 6:
                over += 1
                new_bowler = select_bowler(self.current_inns.bowling_team, self.inn_num, self.current_inns.bowler,
                                           self.current_inns.bowlers, self.current_inns.deliveries)
                deliveries = 0
                cur_ball_num = 0
                print('Over Up. New Bowler: {}'.format(new_bowler.name))
                print('Bowler Figures: {}'.format(
                    self.current_inns.bowler.figures()))
                self.current_inns.over_up(new_bowler)
            cur_ball_num += 1
            ball_counts = self.conduct_delivery(over, cur_ball_num)
            if ball_counts:
                deliveries += 1
        print('Innings Up')
        self.current_inns.display()

    def conduct_chase(self):
        deliveries = 0
        cur_ball_num = 0
        over = 0
        while (not self.current_inns.stop_innings()) and self.current_inns.score <= self.first_innings.score:
            if deliveries == 6:
                over += 1
                cur_ball_num = 0
                new_bowler = select_bowler(self.current_inns.bowling_team, self.inn_num, self.current_inns.bowler,
                                           self.current_inns.bowlers, self.current_inns.deliveries)
                self.current_inns.over_up(new_bowler)
                deliveries = 0
                print('Over Up. New Bowler: {}'.format(new_bowler.name))
                print('Bowler Figures: {}'.format(
                    self.current_inns.bowler.figures()))
            cur_ball_num += 1
            ball_counts = self.conduct_delivery(over, cur_ball_num)
            if ball_counts:
                deliveries += 1
        print('Innings Up')
        self.current_inns.display()

    def find_result(self):
        if self.first_innings.score > self.second_innings.score:
            return '{} win by {} runs'.format(self.first_innings.batting_team.name,
                                              self.first_innings.score - self.second_innings.score)
        if self.first_innings.score < self.second_innings.score:
            return '{} win by {} wickets'.format(self.second_innings.batting_team.name,
                                                 10 - self.second_innings.wickets)
        return 'Tie!'

    def display(self):
        print('1st Innings\n')
        self.first_innings.display()
        print('\n\n2nd Innings\n')
        self.second_innings.display()


def read_team():
    # global full_team
    global player_roles

    # team_name = "Team {}".format(random.randint(0, 10))
    team_name = input('Team Name: ')
    members = []

    with open('data/{}.csv'.format(team_name)) as f:
        for l in f.readlines():
            ps = [x.strip() for x in l.split(',')]

        for p in ps:
            if 'Batsman' in player_roles[p]:
                members.append(Batsman(p))
            elif 'Allrounder' in player_roles[p]:
                members.append(AllRounder(p))
            else:
                members.append(Bowler(p))
        f.close()

    for m in members:
        print('{}'.format(m.name))
    return Team(team_name, members)


def get_toss_result(team1, team2):
    name = input('Who bats first? ')
    if team1.name == name:
        return team1
    return team2


def convert_to_delivery_id(deliveries):
    return float('{}.{}'.format(int(deliveries/6), (deliveries % 6) + 1))


def select_bowler(team, innings, current_bowler, bowled_overs, balls):
    global bowler_over
    over = int(balls/6)
    new_bowler = current_bowler
    bowlers_copy = team.get_bowlers().copy()
    count = 0
    while count < 10 and new_bowler == current_bowler or (new_bowler in bowled_overs and bowled_overs[new_bowler] == 4):
        count += 1
        try:
            bowlers_copy.remove(new_bowler)
        except:
            pass
        b = None
        bcount = 0
        for bwl in bowlers_copy:
            x = bowler_over[(bowler_over.Bowler == bwl.name) & (
                bowler_over.Innings == innings) & (bowler_over.Over == over)]
            if x.shape[0] and x.iloc[0].Count > bcount:
                b, bcount = bwl, x.iloc[0].Count
        new_bowler = b
    if not new_bowler or new_bowler == current_bowler:
        new_bowler = bowlers_copy[random.randint(0, len(bowlers_copy)-1)]
        print('Choosing random bowler {}'.format(new_bowler.name))
    return new_bowler


def select_batsman(team, striker, non_striker, striker_out):
    mem_copy = team.members.copy()
    mem_copy.remove(striker)
    mem_copy.remove(non_striker)
    for m in mem_copy:
        if not m.out:
            return m


player_roles = {}
tmp = pd.read_csv('data/bat_stats.csv')
for _, p in tmp.iterrows():
    player_roles[str(p.Name).strip()] = p.Role


del tmp

tmp = pd.read_csv('data/bowl_stats.csv')
for _, p in tmp.iterrows():
    player_roles[str(p.Name).strip()] = p.Role


del tmp

team1 = read_team()
team2 = read_team()

bats_first = get_toss_result(team1, team2)
chasers = team1
if team1.name == bats_first.name:
    chasers = team2

bowler_over = pd.read_csv('data/bowler_over_stats.csv')
bat_clusters = {}
bowl_clusters = {}
df_bat = pd.read_csv('data/bat_clusters.csv')
df_bowl = pd.read_csv('data/bowl_clusters.csv')

for _, bat in df_bat.iterrows():
    bat_clusters[bat.Name] = bat.Cluster

for _, bowl in df_bowl.iterrows():
    bowl_clusters[bowl.Name] = bowl.Cluster

match = Match(bats_first, chasers)
match.start_match()
match.conduct_first_innings()

del df_bat
del df_bowl

match.start_chase()
match.conduct_chase()

result = match.find_result()
print('{} vs {}. The result is: {}'.format(team1.name, team2.name, result))
