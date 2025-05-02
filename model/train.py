import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


df = pd.read_csv('data/dataset.csv')
features = [c for c in df.columns if c not in ['ticker', 'date', 'close_raw', 'outperformed', 'quarter_id']]

# Apply partial dropout per quarter
def apply_partial_dropout(df, k=4):
    if k == 0:
        return df
    return df.groupby('quarter_id').apply(lambda group: group.sample(n=min(k, len(group)))).reset_index(drop=True)

def prepare_model_data(df):
    df = apply_partial_dropout(df, k=0)
    X = df[features].values
    y = df['outperformed'].values
    return X, y

def train_logistic_regression(X_train, X_test, y_train, y_test):
    model = LogisticRegression(penalty='l2', solver='liblinear')
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc:.4f}")
    return model

X, y = prepare_model_data(df)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = train_logistic_regression(X_train, X_test, y_train, y_test)
joblib.dump(model, 'models/l2.pkl')