import yaml
import csv
import glob
import os

def getDictFromYaml(filename):
    with open(filename, 'r') as stream:
        try:
            content = yaml.load(stream)
            stream.close()
            return content
        except yaml.YAMLError as exc:
            print("Error: ", exc)
            return {}


class ball(object):
    def __init__(self, id, innings, batsman, bowler, runs, extra_runs, extra_type, wicket_type, batsman_score, bowler_over):
        self.id = id
        self.innings = innings
        self.batsman = batsman
        self.bowler = bowler
        self.runs = runs
        self.extra_runs = extra_runs
        self.extra_type = extra_type
        self.wicket_type = wicket_type
        self.batsman_score = batsman_score
        self.bowler_over = bowler_over

    def __str__(self):
        return '{},{},{},{},{},{},{},{},{},{}'.format(self.id, self.innings, self.batsman,
                                                self.bowler, self.runs,
                                                self.extra_runs, self.extra_type, int(self.wicket_type),
                                                self.batsman_score, self.bowler_over)

def parse_all_yaml(yaml_dir='yaml', out_file='data/all_deliveries.csv'):
    balls = []
    for filename in glob.glob('{}/*.yaml'.format(yaml_dir)):
        match = getDictFromYaml(filename)
        print('Parsing file ' + filename)
        batsman_score = {}
        bowler_over = {}
        for match_details in match["innings"]:
            for innings in match_details:
                for delivery in match_details[innings]['deliveries']:
                    for ball_id in delivery:
                        details = delivery[ball_id]
                        extra_runs = 0
                        extra_type = None
                        if 'extras' in details:
                            extra_runs = details['runs']['extras']
                            extra_type = list(details['extras'].keys())[0]

                        wicket_type = None
                        if 'wicket' in details:
                            # wicket_type = 1
                            wicket_type = details['wicket']['kind']
                        
                        if details['batsman'] in batsman_score:
                            batsman_score[details['batsman']] += details['runs']['batsman']
                        else:
                            batsman_score[details['batsman']] = details['runs']['batsman']
                        
                        bwl = details['bowler']
                        if not bwl in bowler_over:
                            bowler_over[bwl] = set()
                        bowler_over[bwl].add(str(ball_id).split('.')[0])

                        balls.append(
                            ball(ball_id, innings, details['batsman'], details['bowler'], details['runs']['batsman'],
                                extra_runs, extra_type, wicket_type, batsman_score[details['batsman']], len(bowler_over[bwl])))


    fp = out_file
    print("Saving file {}".format(fp))
    with open(fp, 'w') as file:
        file.write('{}\n'.format('Delivery,Innings,Batsman,Bowler,Runs,Extras,ExtraType,Wicket,BatsmanScore,BowlerOver'))
        for b in balls:
            file.write("%s\n" % b)

    file.close()

if __name__ == '__main__':
    parse_all_yaml()