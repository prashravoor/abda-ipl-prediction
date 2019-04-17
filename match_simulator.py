import random

class Player:
    def __init__(self, name, is_batsman, is_bowler):
        self.name = name
        self.is_batsman = is_batsman
        self.is_bowler = is_bowler

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
        self.bowlers = set()
        # Role redressal - all batting team are batsmen
        batting_team_members = [Batsman(x.name) for x in batting_team.members]
        bowling_team_members = [Bowler(x.name) for x in bowling_team.members]
        self.batting_team = Team(batting_team.name, batting_team_members)
        self.bowling_team = Team(bowling_team.name, bowling_team_members)

    def stop_innings(self):
        if self.wickets == 10 or self.deliveries == 12:
            return True
        return False

    def runs_scored(self, runs):
        self.score += runs
        self.deliveries += 1
        self.striker.runs_scored(runs)
        self.bowler.runs_conceded(runs)
        if (runs % 2 != 0): # Rotate strike
            self.striker, self.non_striker = self.non_striker, self.striker

    def extras_conceded(self, extras, extra_ball=False):
        self.score += extras
        self.extras += extras
        self.bowler.extras_conceded(extras, extra_ball)
        if not extra_ball:
            self.deliveries += 1
            self.striker.num_deliveries += 1
        #if not (extras % 2 == 0): # Rotate strike
        #    self.striker, self.non_striker = self.non_striker, self.striker

    def over_up(self, new_bowler):
        self.bowlers.add(new_bowler)
        self.bowler = new_bowler
        self.striker,self.non_striker = self.non_striker, self.striker

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
            self.striker,self.non_striker = self.non_striker,self.striker
        batsman.start_play()
        return b

    def start_innings(self, bowler):
        self.bowler = bowler
        self.bowlers.add(bowler)
        self.striker = self.batting_team.members[0]
        self.non_striker = self.batting_team.members[1]
        self.striker.start_play()
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
        print('Extras: {}\nTotal Score: {} - {}'.format(self.extras, self.score, self.wickets))
        print('Bowling Team: {}'.format(self.bowling_team.name))
        for bowler in self.bowlers:
            detail = bowler.name
            detail += ' ' + bowler.figures()
            print(detail)

        print('Overs: {}.{}'.format(int(self.deliveries/6), self.deliveries % 6))


class Match:
    def __init__(self, first_bat, chaser):
        self.first_innings = Innings(first_bat, chaser)
        self.second_innings = Innings(chaser, first_bat)
        self.current_inns = None

    def start_match(self):
        bowler = select_bowler(self.first_innings.bowling_team, None)
        self.first_innings.start_innings(bowler)
        self.current_inns = self.first_innings
        print('Starting the Match! Team Batting First: {}, First Bowler: {}'.format(self.current_inns.batting_team.name, bowler.name))

    def start_chase(self):
        bowler = select_bowler(self.second_innings.bowling_team, None)
        self.second_innings.start_innings(bowler)
        self.current_inns = self.second_innings
        print('Starting the Chase! First Bowler: {}'.format(bowler.name))

    def conduct_delivery(self):
        ball_counts = True
        wicket, wicket_type = predict_wicket(self.current_inns.bowler,
                                            self.current_inns.striker,
                                            self.current_inns.deliveries)
        runs, num_runs = predict_runs(self.current_inns.bowler,
                                    self.current_inns.striker,
                                    self.current_inns.deliveries)
        extras, extra_type, extra_runs = predict_extras(self.current_inns.bowler,
                                            self.current_inns.striker,
                                            self.current_inns.deliveries)
        event = max(wicket, runs, extras)
        if event == wicket:
            crossover = False
            striker = True
            if wicket_type in ['caught', 'run out']:
                striker = (random.random() < 0.5)
                crossover = (random.random() < 0.5)

            new_batsman = select_batsman(self.current_inns.batting_team,
                                        self.current_inns.striker,
                                        self.current_inns.non_striker, striker)
            batsman = self.current_inns.wicket(wicket_type, new_batsman, striker, crossover)
            print('Wicket Falls! Out Batsman: {}, Bowler: {}, Crossover: {}, New Batsman: {}'.format(
                                        batsman.name,
                                        self.current_inns.bowler.name,
                                        crossover,
                                        new_batsman.name))
            print('Batsman Figures: {}'.format(batsman.figures()))
        elif event == extras:
            extra_ball = False
            if extra_type in ['wides', 'noballs']:
                extra_ball = True
                ball_counts = False
            self.current_inns.extras_conceded(extra_runs, extra_ball)
            print('Extras! Bowler: {}, Extra Type: {}, Runs: {}'.format(
                                        self.current_inns.bowler.name,
                                        extra_type,
                                        extra_runs))
        else:
            print('Runs Scored. Batsman: {}, Bowler: {}, Num Runs: {}'.format(self.current_inns.striker.name,
                                    self.current_inns.bowler.name, num_runs))
            self.current_inns.runs_scored(num_runs)
        print('Current Innings Score: {}'.format(self.current_inns.score))
        return ball_counts

    def conduct_first_innings(self):
        deliveries = 0
        while not self.current_inns.stop_innings():
            if deliveries == 6:
                new_bowler = select_bowler(self.current_inns.bowling_team, self.current_inns.bowler)
                deliveries = 0
                print('Over Up. New Bowler: {}'.format(new_bowler.name))
                print('Bowler Figures: {}'.format(self.current_inns.bowler.figures()))
                self.current_inns.over_up(new_bowler)
            ball_counts = self.conduct_delivery()
            if ball_counts:
                deliveries += 1
        print('Innings Up')
        self.current_inns.display()

    def conduct_chase(self):
        deliveries = 0
        while (not self.current_inns.stop_innings()) and self.current_inns.score <= self.first_innings.score:
            if deliveries == 6:
                new_bowler = select_bowler(self.current_inns.bowling_team, self.current_inns.bowler)
                self.current_inns.over_up(new_bowler)
                deliveries = 0
            ball_counts = self.conduct_delivery()
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
                10  - self.second_innings.wickets)
        return 'Tie!'

    def display(self):
        print('1st Innings\n')
        self.first_innings.display()
        print('\n\n2nd Innings\n')
        self.second_innings.display()

def read_team():
    team_name = "Team {}".format(random.randint(0,10))
    print('Team Name: {}'.format(team_name))
    members = []
    for _ in range(11):
        name = 'Player {}'.format(random.randint(0,100))
        if random.random() < 0.5:
            members.append(Batsman(name))
        else:
            members.append(Bowler(name))
    for m in members:
        print('{}'.format(m.name))
    return Team(team_name, members)

def get_toss_result(team1, team2):
    return team1

def select_bowler(team, current_bowler):
    return team.members[random.randint(0,10)]

def select_batsman(team, striker, non_striker, striker_out):
    return team.members[random.randint(0,10)]

def predict_wicket(bowler, batsman, deliveries):
    return random.random(), ""

def predict_extras(bowler, batsman, deliveries):
    return random.random(), "", random.randint(0,4)

def predict_runs(bowler, batsman, deliveries):
    return random.random(), random.randint(0,6)

team1 = read_team()
team2 = read_team()

bats_first = get_toss_result(team1, team2)
chasers = team1
if team1.name == bats_first.name:
    chasers = team2

match = Match(bats_first, chasers)
match.start_match()
match.conduct_first_innings()

match.start_chase()
match.conduct_chase()

result = match.find_result()
print('{} vs {}. The result is: {}'.format(team1.name, team2.name, result))