__author__ = 'Thushan Ganegedara'

import xgboost as xgb
import numpy as np
import pandas as pd

def divide_test_valid(train_data):

    '''
            0th class 6.58, 1st class 2.58, 2nd class 1 (ratios)
    '''
    import csv

    my_train_ids = []
    my_valid_ids = []
    my_train_ids_v2 = [[],[],[]]

    data_x = []
    data_y = []
    valid_x,valid_y = [],[]
    data_x_v2 = [[],[],[]]

    tr_ids,tr_x, tr_y = train_data

    for i in range(len(tr_x)):
        # first 2 columns are ID and location
        output = int(tr_y[i])
        data_x_v2[output].append(tr_x[i])
        my_train_ids_v2[output].append(tr_ids[i])

    valid_size = 500
    full_rounds = 1
    orig_class_2_length = len(data_x_v2[2])
    for _ in range(orig_class_2_length):
        rand = np.random.random()
        if rand>=0.9 or len(valid_x)>valid_size:
            for _ in range(4) :
                data_x.append(data_x_v2[0][-1])
                data_x_v2[0].pop()
                data_y.append(0)
                my_train_ids.append(my_train_ids_v2[0][-1])
                my_train_ids_v2[0].pop()

            for _ in range(2):
                data_x.append(data_x_v2[1][-1])
                data_x_v2[1].pop()
                data_y.append(1)
                my_train_ids.append(my_train_ids_v2[1][-1])
                my_train_ids_v2[1].pop()

            data_x.append(data_x_v2[2][-1])
            data_x_v2[2].pop()
            data_y.append(2)
            my_train_ids.append(my_train_ids_v2[2][-1])
            my_train_ids_v2[2].pop()
            full_rounds += 1

        elif len(valid_x)<valid_size and rand<0.1:

            for _ in range(2):
                valid_x.append(data_x_v2[0][-1])
                data_x_v2[0].pop()
                valid_y.append(0)
                my_valid_ids.append(my_train_ids_v2[0][-1])
                my_train_ids_v2[0].pop()

            for _ in range(1):
                valid_x.append(data_x_v2[1][-1])
                data_x_v2[1].pop()
                valid_y.append(1)
                my_valid_ids.append(my_train_ids_v2[1][-1])
                my_train_ids_v2[1].pop()

            valid_x.append(data_x_v2[2][-1])
            data_x_v2[2].pop()
            valid_y.append(2)
            my_valid_ids.append(my_train_ids_v2[2][-1])
            my_train_ids_v2[2].pop()

            full_rounds += 1

    for j in range(len(data_x_v2[0])):
        data_x.append(data_x_v2[0][j])
        data_y.append(0)
        my_train_ids.append(my_train_ids_v2[0][j])

    for j in range(len(data_x_v2[1])):
        data_x.append(data_x_v2[1][j])
        data_y.append(1)
        my_train_ids.append(my_train_ids_v2[1][j])

    for j in range(len(data_x_v2[2])):
        data_x.append(data_x_v2[2][j])
        data_y.append(2)
        my_train_ids.append(my_train_ids_v2[2][j])

    train_set = (my_train_ids,data_x,data_y)
    valid_set = (my_valid_ids,valid_x,valid_y)

    print('Train: ',len(train_set[0]),' x ',len(train_set[1][0]))
    print('Valid: ',len(valid_set[0]),' x ',len(valid_set[1][0]))

    return train_set,valid_set


def load_teslstra_data_v3(train_file,test_file,drop_col=None):

    tr_data = pd.read_csv(train_file)
    test_data = pd.read_csv(test_file)

    tr_ids = tr_data[['id']]
    tr_x = tr_data.ix[:,1:-1]
    tr_y = tr_data.ix[:,-1]

    test_ids = test_data[['id']]
    test_x = test_data.ix[:,1:]
    correct_order_test_ids = []
    import csv
    with open('test.csv', 'r',newline='') as f:
        reader = csv.reader(f)
        for i,row in enumerate(reader):
            if i==0:
                continue
            correct_order_test_ids.append(int(row[0]))

    if drop_col is not None:
        for drop_col in drop_col:
            header = list(tr_x.columns.values)
            to_drop = [i for i,v in enumerate(header) if drop_col in v]

            tr_x.drop(tr_x.columns[to_drop],axis=1,inplace=True)
            test_x.drop(test_x.columns[to_drop],axis=1,inplace=True)

    return (tr_ids,tr_x,tr_y), (test_ids,test_x), correct_order_test_ids

class MyXGBClassifier(object):

    def __init__(self, n_rounds=100, **params):
        self.params = params
        self.params.update({'booster':'gbtree'})
        self.params.update({'silent':1})
        self.params.update({'objective': 'multi:softprob'})
        self.params.update({'num_class': 3})
        self.params.update({'eval_metric':'mlogloss'})
        self.clf = None
        self.n_rounds = n_rounds
        self.dtrain = None

    def fit(self, X, Y):
        num_boost_round = self.n_rounds
        self.dtrain = xgb.DMatrix(X, label=Y)
        # don't use iterative train if using early_stop
        self.clf = xgb.train(params=self.params, dtrain=self.dtrain, num_boost_round=num_boost_round)

    def predict(self, X):
        Y = self.clf.predict_proba(X)
        y = np.argmax(Y, axis=1)
        return np.array(y)

    def predict_proba(self, X):
        dtest = xgb.DMatrix(X)
        return self.clf.predict(dtest)

    def get_params(self, deep=True):
        return self.params

    def set_params(self, **params):
        self.params.update(params)
        return self

    def logloss(self, X, Y):
        return logloss(self,X,Y)

    def score(self, X, Y):
        return 1 / logloss(self,X, Y)

from sklearn.grid_search import GridSearchCV

def logloss(est, X, Y):

    probs = est.predict_proba(X)
    logloss = 0.0
    for i in range(len(Y)):
        tmp_y = [0.,0.,0.]
        tmp_y[Y[i]]=1.
        v_probs = probs[i]
        if any(v_probs)==1.:
            v_probs = np.asarray([np.max([np.min([p,1-1e-15]),1e-15]) for p in v_probs])

        logloss += np.sum(np.asarray(tmp_y)*np.log(np.asarray(v_probs)))
    logloss = -logloss/len(Y)

    return logloss

def scorer_logloss(est, X, Y):
    return 1./logloss(est,X, Y)

def run_grid_search(params,X,Y,n_rounds,get_original=False):

    clf = MyXGBClassifier(n_rounds=n_rounds,eta=0.2,max_depth=10,subsample=0.9,colsample_bytree=0.9)

    gridsearch = GridSearchCV(clf, params, scoring=scorer_logloss, n_jobs=10, cv=3, refit=True)

    print('Fitting (Grid Search) ...')
    gridsearch.fit(X,Y)
    report(gridsearch.grid_scores_)
    return gridsearch

from operator import itemgetter
def report(grid_scores, n_top=3):
    top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
              score.mean_validation_score,
              np.std(score.cv_validation_scores)))
        print("Parameters: {0}".format(score.parameters))
        print("")

from sklearn.ensemble import ExtraTreesClassifier
if __name__ == '__main__':

    f_names = ['features_dl_all']
    mean_test_logloss = []
    run = 'crossvalidation' # gridsearch or crossvalidation
    for f in f_names:
        tr_data, test_data, correct_ids = load_teslstra_data_v3(f+'_train.csv',f+'_test.csv',None)
        tr_ids,tr_x,tr_y = tr_data
        ts_ids,ts_x = test_data


        print('Train: ', tr_x.shape)
        print('Test: ', ts_x.shape)

        if run == 'gridsearch':
            parameters = {
                'eta':[0.1,0.15,0.2],
                'max_depth': [5, 10, 20],
                'lambda': [0.9, 0.99],
                'alpha': [0.9,0.99]
                #'max_delta_step': [0]
            }

            clf = run_grid_search(parameters,tr_x.as_matrix(),tr_y.as_matrix(),70)
        elif run == 'crossvalidation':
            param = {}
            param['objective'] = 'multi:softprob'
            param['booster'] = 'gbtree'
            param['eta'] = 0.03  # high eta values give better perf
            param['max_depth'] = 10
            param['silent'] = 1
            param['lambda'] = 0.9
            param['alpha'] = 0.9
            #param['nthread'] = 4
            param['subsample']=0.9
            param['colsample_bytree']=0.9
            param['num_class'] = 3
            param['eval_metric']='mlogloss'
            param['num_rounds'] = 1500

            tr_x = np.asarray(tr_x)
            ts_x = np.asarray(ts_x)

            weights = []
            for ex in tr_y:
                if ex==0:
                    weights.append(1.0)
                elif ex==1:
                    weights.append(1.0)
                else:
                    weights.append(1.0)

            clf = ExtraTreesClassifier()
            clf = clf.fit(tr_x, tr_y)
            fimp = np.asarray(clf.feature_importances_)
            ord_feature_idx = list(reversed(np.argsort(fimp)))
            fimp_thresh = 1.
            # need to sort, else hard to perform delete
            train_feature_idx = ord_feature_idx[int(fimp_thresh*len(ord_feature_idx)):]
            train_feature_idx.sort()
            for fidx in reversed(train_feature_idx):
                tr_x = np.delete(tr_x,fidx,axis=1)
                ts_x = np.delete(ts_x,fidx,axis=1)

            print("After Transformation ...")
            print('Train: ',tr_x.shape)
            print('Test: ',ts_x.shape)

            dtrain = xgb.DMatrix(tr_x, label=tr_y, weight=weights)
            history = xgb.cv(param,dtrain,param['num_rounds'],nfold=5,metrics={'mlogloss'})
            print(np.min(history['test-mlogloss-mean']),' at ',np.argmin(history['test-mlogloss-mean']),' iteration')

        mean_test_logloss.append(np.min(history['test-mlogloss-mean']))


        #print(f+', Avg mlogloss: ',np.mean(mean_test_logloss))
#Mean validation score: 1.815 (std: 0.021)
#Parameters: {'max_depth': 5, 'eta': 0.2, 'alpha': 0.9, 'lambda': 0.9}