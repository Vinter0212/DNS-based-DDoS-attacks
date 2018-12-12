import pandas as pd
import numpy as np
from sklearn import cross_validation,svm

#%%
df = pd.read_csv('./data/data.csv')
X = df[["forward_packet_count","backward_packet_count","backward_flow_volume"]].values
Y = np.array(df['DDoS attack'])

#%%
X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, Y, test_size=0.2)
clf = svm.SVC()
clf.fit(X_train,y_train)
#%%
accuracy = clf.score(X_test,y_test)
print(accuracy)
