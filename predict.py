from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import hashlib
from sklearn.model_selection import train_test_split
import pickle

fit = {}
feature_names = ['Delivery', 'Innings', 'Batsman', 'Bowler', 'BowlerOver', 'BatsmanScore']
def load_model(feature, data_dir='data'):
    global fit
    try:
        with open('{}/{}_model.dmp'.format(data_dir, feature), 'rb') as f:
            fit[feature] = pickle.load(f)
            f.close()
    except:
        if feature == 'Runs':
            fit[feature] = KNeighborsClassifier(n_neighbors=25)
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
    for _,row in df.iterrows():
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
    train_data = train.loc[:,feature_names]
    test_data = test.loc[:,feature_names]
    test_target = test[feature]

    train_target = train[feature]
    load_model(feature, out_file_dir)
    fit[feature] = fit[feature].fit(train_data, train_target)
    save_model(feature, out_file_dir)

    y_pred = fit[feature].predict(test_data) # predict_feature(feature, train_data, test_data, gnb)

    print('Prediction accuracy for Feature {}: {}'.format(feature, ((y_pred == test_target).sum())/len(y_pred)))

def predict_delivery(attributes, feature):
    if not feature in fit:
        load_model(feature)
    d = pd.DataFrame([attributes],columns=feature_names)
    # d = pd.concat([d, attributes], ignore_index=True)
    return fit[feature].predict(d)

def train_features(df_name='data/cluster_deliveries.csv', features=['Result', 'Runs', 'Wicket', 'ExtraType', 'Extras']):
    df = pd.read_csv(df_name)
    # df = df.iloc[:,1:]
    # df = df.drop_duplicates()
    df = create_result_col(df)

    for feature in features:
        train_and_save_model(df, feature)

if __name__ == '__main__':
    train_features()
