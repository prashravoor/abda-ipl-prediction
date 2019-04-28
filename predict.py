from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
import pandas as pd
import numpy as np
import hashlib
from sklearn.model_selection import train_test_split
import pickle
import random

fit = {}
feature_names = ['Delivery', 'Innings', 'Batsman',
                 'Bowler', 'BowlerOver', 'Wickets', 'TeamScore']
result_priors = [.2, .6, .2]  # Extras, Runs, Wicket


def load_model(feature, data_dir='data'):
    global fit
    try:
        with open('{}/{}_model.dmp'.format(data_dir, feature), 'rb') as f:
            fit[feature] = pickle.load(f)
            f.close()
    except:
        if feature == 'Result':
            fit[feature] = MultinomialNB(class_prior=result_priors)
        else:
            fit[feature] = GaussianNB()


def save_model(feature, out_file_dir='data'):
    with open('{}/{}_model.dmp'.format(out_file_dir, feature), 'wb') as fid:
        pickle.dump(fit[feature], fid)
        fid.close()


def filter_by_feature(df, feature):
    if feature == 'Extras' or feature == 'ExtraType':
        return df.loc[df['Result'] == 'Extras']
    return df.loc[df['Result'] == feature]


def create_result_col(df):
    result = []
    for _, row in df.iterrows():
        if row['Wicket'] != 'None':
            result.append('Wicket')
        elif row['ExtraType'] != 'None':
            result.append('Extras')
        else:
            result.append('Runs')
    df['Result'] = result
    return df


def train_and_save_model(df, feature, test_size=0.3, out_file_dir='data'):
    global fit
    if not feature == 'Result':
        df_f = filter_by_feature(df, feature)
    else:
        df_f = df

    train, test = train_test_split(df_f, test_size=test_size)
    # feature = 'Runs'
    train_data = train.loc[:, feature_names]
    test_data = test.loc[:, feature_names]
    test_target = test[feature]
    train_target = train[feature]

    load_model(feature, out_file_dir)

    fit[feature] = fit[feature].fit(train_data, train_target)
    save_model(feature, out_file_dir)

    # predict_feature(feature, train_data, test_data, gnb)
    y_pred = fit[feature].predict(test_data)

    print('Prediction accuracy for Feature {}: {}'.format(
        feature, ((y_pred == test_target).sum())/len(y_pred)))


class RingBuffer:
    def __init__(self, size):
        self.data = [None for i in range(size)]

    def append(self, x):
        self.data.pop(0)
        self.data.append(x)

    def get(self):
        return self.data

    def count(self, el):
        c = 0
        for e in self.data:
            if el == e:
                c += 1
        return c


prev_result = RingBuffer(12)
prev_runs = RingBuffer(12)


def predict_delivery(attributes, feature):
    global df
    global is_loaded
    # d = pd.concat([d, attributes], ignore_index=True)
    if not is_loaded:
        df = pd.read_csv('data/cluster_deliveries_with_result.csv')
        is_loaded = True

    if not feature in fit:
        load_model(feature)
    d = pd.DataFrame([attributes], columns=feature_names)

    global prev_result
    if feature == 'Result':
        r = fit[feature].predict_proba(d)[0]
        e = prev_result.count('Extras') + 1
        w = prev_result.count('Wicket') + 1
        if e > 0:
            r[0] = r[0]/e

        if w > 1:
            r[2] = r[2]/(w*w*w)
        # print(d, r)
        # Threshold for Wicket is 10%, Extra is 22%
        random.seed()
        wick_thresh = random.uniform(0.07, 0.12)
        if r[2] >= wick_thresh:
            prev_result.append('Wicket')
            return 'Wicket'
        if r[0] >= .22:
            prev_result.append('Extras')
            return 'Extras'
        prev_result.append('Runs')
        return 'Runs'
    elif feature == 'Runs':
        r = fit[feature].predict_proba(d)[0]
        for i in range(0, 7):
            c = prev_runs.count(i) + 1
            if c > 1:
                r[i] /= (c*16)
        rs = np.argmax(r, axis=0)
        prev_runs.append(rs)
        return rs
    else:
        return fit[feature].predict(d)


def train_features(df_name='data/cluster_deliveries.csv', features=['Result', 'Runs', 'Wicket', 'ExtraType', 'Extras']):
    global df
    df = pd.read_csv(df_name)
    # df = df.iloc[:,1:]
    # df = df.drop_duplicates()
    df = create_result_col(df)
    df.to_csv('data/cluster_deliveries_with_result.csv',
              index=False, header=True)

    for feature in features:
        train_and_save_model(df, feature)


df = None
is_loaded = False
if __name__ == '__main__':
    train_features()
