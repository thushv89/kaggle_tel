__author__ = 'Thushan Ganegedara'

import csv
import collections
import numpy as np

train_data = collections.defaultdict()
all_locs = []
with open('train.csv', 'r',newline='') as f:
    reader = csv.reader(f)

    for i,row in enumerate(reader):
        if i==0:
            continue
        data_row = []
        id,loc,sev = None,None,None

        for j,col in enumerate(row):
            if j==0:
                id = col
            elif j==1:
                loc = int(col[9:])
                all_locs.append(int(col[9:]))
            elif j==2:
                sev = int(col)
        train_data[id]=[loc,sev]

max_loc = np.max(all_locs)
train_count = len(train_data)

test_data = collections.defaultdict()
with open('test.csv', 'r',newline='') as f:
    reader = csv.reader(f)

    for i,row in enumerate(reader):
        if i==0:
            continue
        data_row = []
        id,loc = None,None

        for j,col in enumerate(row):
            if j==0:
                id = col
            elif j==1:
                loc = int(col[9:])
                all_locs.append(int(col[9:]))
        test_data[id]=[loc]

feature_data = collections.defaultdict()
all_features = []
max_per_feature = collections.defaultdict()
feature_count = collections.defaultdict()

with open('log_feature.csv', 'r',newline='') as f:
    reader = csv.reader(f)

    for i,row in enumerate(reader):
        if i==0:
            continue
        data_row = []
        id,feature,vol = None,None,None


        for j,col in enumerate(row):
            if j==0:
                id = col
            elif j==1:
                feature = int(col[8:])
                all_features.append(int(col[8:]))
            elif j==2:
                vol = int(col)

        if feature in feature_count:
            feature_count[feature] += 1
        else:
            feature_count[feature] = 1

        if id in feature_data:
            feature_data[id].append([feature,vol])
        else:
            feature_data[id]=[[feature,vol]]

        if feature in max_per_feature:
            if vol > max_per_feature[feature]:
                max_per_feature[feature] = vol
        else:
            max_per_feature[feature] = vol


important_features=[] # based on the values count for each feature

for k,v in feature_count.items():
    if v > 1:
        important_features.append(k)
max_feature = len(important_features)

severity_data = collections.defaultdict()
all_severity = []

with open('severity_type.csv', 'r',newline='') as f:
    reader = csv.reader(f)

    for i,row in enumerate(reader):
        if i==0:
            continue
        data_row = []
        id,sev = None,None

        for j,col in enumerate(row):
            if j ==0:
                id = col
            elif j==1:
                sev = int(col[13:])
                all_severity.append(sev)
        severity_data[id]=[sev]

max_severity = np.max(all_severity)

event_data = collections.defaultdict()
all_event = []

with open('event_type.csv', 'r',newline='') as f:
    reader = csv.reader(f)

    for i,row in enumerate(reader):
        if i==0:
            continue
        data_row = []
        id,event = None,None

        for j,col in enumerate(row):
            if j ==0:
                id = col
            elif j == 1:
                event = int(col[11:])
                all_event.append(event)
        if id in event_data:
            event_data[id].append(event)
        else:
            event_data[id] = [event]

max_event = np.max(all_event)

resource_data = collections.defaultdict()
all_resource =[]
with open('resource_type.csv', 'r',newline='') as f:
    reader = csv.reader(f)

    for i,row in enumerate(reader):
        if i==0:
            continue
        data_row = []
        id,res = None,None

        for j,col in enumerate(row):
            if j ==0:
                id = col
            elif j == 1:
                res = int(col[14:])
                all_resource.append(res)
        if id in resource_data:
            resource_data[id].append(res)
        else:
            resource_data[id] = [res]

max_res = np.max(all_resource)

'''
#concat all data
all_data = collections.defaultdict()
all_out = collections.defaultdict()
all_feature_val = collections.defaultdict()
for k,v in train_data.items():
    row = [v[0]] # we need to add the output to a different dic
    all_out[k] = v[1]
    if k in feature_data:
        v.extend(feature_data[k][0])
        #all_feature_val[k] = feature_data[k][1]
    if k in severity_data:
        v.extend(severity_data[k])
    if k in event_data:
        v.extend(event_data[k])
    if k in resource_data:
        v.extend(resource_data[k])

    all_data[k] = v
    assert len(v)==7'''

# features start with 1
# severity start with 1
# event starts with 1
# resource starts with 1
# 2 for id and location
neuron_count = 2 + (max_feature) + (max_severity) + (max_event) + (max_res)
print('neuron count: ',neuron_count)

def turn_to_vec(indices,max_val,val=1):
    row = [0 for _ in range(max_val+1)]
    for i in indices:
        row[i] = val
    return row

valid_set = []



def write_file(file_name,train_data,feature_data,severity_data,event_data,resource_data,include,isTrain=True,noise=False):
    if isTrain:
        file_name += '_train.csv'
    else:
        file_name += '_test.csv'

    doOnce = False
    with open(file_name, 'w',newline='') as f:
        writer = csv.writer(f)
        for k,v in train_data.items():

            if 'id' in include:
                write_row = [k]
            else:
                write_row = []

            loc_thresh = 50 # 10 will give 110 element vec, 100 will give 11 element vec
            if 'loc' in include:
                if 's' in include['loc'] :
                    if 'n' in include['loc']:
                        loc_vec = [v[0]*1.0/max_loc]
                elif 'v' in include['loc']:
                    from math import floor
                    val_for_v0 = float((v[0]*1.0 % loc_thresh)/loc_thresh)
                    if loc_thresh!=1:
                        loc_vec = turn_to_vec([floor(v[0]/loc_thresh)],floor(max_loc*1./loc_thresh),val_for_v0)
                    else:
                        loc_vec = turn_to_vec([v[0]],max_loc,1)


            if 'feat' in include:
                f_list = feature_data[k]
                feature_vec = [0 for _ in range(max_feature+1)]
                # list[0] is feature id and list[1] is corresponding value
                for list in f_list:
                    if list[0] in important_features:
                        if 'n' in include['feat']:
                            feature_vec[important_features.index(list[0])] = list[1]*1.0/max_per_feature[list[0]]
                            assert feature_vec[important_features.index(list[0])]<=1
                        else:
                            feature_vec[important_features.index(list[0])] = list[1]

            if 'sev' in include:
                if 's' in include['sev']:
                    if 'n' in include['sev']:
                        sev_vec = [severity_data[k]*1.0/max_severity]
                    else:
                        sev_vec = [severity_data[k]]
                elif 'v' in include['sev']:
                    sev_vec = turn_to_vec(severity_data[k],max_severity)

            if 'eve' in include:
                if 's' in include['eve']:
                    raise NotImplementedError
                elif 'v' in include['sev']:
                    event_vec = turn_to_vec(event_data[k],max_event)

            if 'res' in include:
                if 's' in include['res']:
                    raise NotImplementedError
                elif 'v' in include['res']:
                    res_vec = turn_to_vec(resource_data[k],max_res)


            if not doOnce:
                header = ['id']
                header.extend(['loc_'+str(i) for i in range(len(loc_vec))])
                header.extend(['feat_'+str(i) for i in range(len(feature_vec))])
                header.extend(['sev_'+str(i) for i in range(len(sev_vec))])
                header.extend(['eve_'+str(i) for i in range(len(event_vec))])
                header.extend(['res_'+str(i) for i in range(len(res_vec))])
                if isTrain:
                    header.append('out')
                writer.writerow(header)
                doOnce = True

            
            write_row.extend(loc_vec)
            write_row.extend(feature_vec)
            write_row.extend(sev_vec)
            write_row.extend(event_vec)
            write_row.extend(res_vec)

            if noise:
                noise_vec = np.random.binomial(1,0.25,(len(write_row)))*np.random.random((len(write_row)))*0.1
                write_row[1:] = [np.min([x+y,1.]) for x,y in zip(write_row[1:],noise_vec.tolist())]
            if isTrain:
                out = v[1]
                write_row.extend([out])

            writer.writerow(write_row)

def select_features(train_file,test_file,remove_header):

    tr_ids, train_data_x,train_data_y = [],[],[]
    ts_ids, test_data_x,test_data_y = [],[],[]

    with open(train_file, 'r',newline='') as f:
        reader = csv.reader(f)

        for i,row in enumerate(reader):
            if i==0 and remove_header:
                continue
            else:
                tr_ids.append(int(row[0]))
                train_data_x.append([float(x) for x in row[1:-1]])
                train_data_y.append(int(row[-1]))

    with open(test_file, 'r',newline='') as f:
        reader = csv.reader(f)

        for i,row in enumerate(reader):
            if i==0 and remove_header:
                continue
            else:
                ts_ids.append(int(row[0]))
                test_data_x.append([float(x) for x in row[1:]])

    from sklearn.svm import LinearSVC
    from sklearn.feature_selection import SelectFromModel

    lsvc = LinearSVC(C=0.3, penalty="l1", dual=False).fit(
            np.asarray(train_data_x,dtype=np.float32),np.asarray(train_data_y,dtype=np.int32)
    )
    model = SelectFromModel(lsvc, prefit=True)
    train_x_new = model.transform(np.asarray(train_data_x,dtype=np.float32))
    test_x_new = model.transform(np.asarray(test_data_x,dtype=np.float32))


    with open('features_svm_train.csv', 'w',newline='') as f:
        writer = csv.writer(f)

        for i,tr in enumerate(train_x_new.tolist()):
            tr_row = [tr_ids[i]]
            tr_row.extend(tr)
            tr_row.append(train_data_y[i])
            writer.writerow(tr_row)

    with open('features_svm_test.csv', 'w',newline='') as f:
        writer = csv.writer(f)

        for i,ts in enumerate(test_x_new.tolist()):
            ts_row = [ts_ids[i]]
            ts_row.extend(ts)

            writer.writerow(ts_row)



# s for single value
# v for vector
# n for nomarlize

include = {'id':'s','loc':'v','feat':'vn','sev':'v','eve':'v','res':'v'}
file_name = 'features_2'


write_file(file_name,train_data,feature_data,severity_data,event_data,resource_data,include,True,False)
write_file(file_name,test_data,feature_data,severity_data,event_data,resource_data,include,False,False)

#select_features('features_modified_train.csv','features_modified_test.csv',True)