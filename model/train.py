import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import os


os.makedirs('models', exist_ok=True)

df = pd.read_csv('data/dataset.csv')
features = [c for c in df.columns if c not in ['ticker', 'date', 'close_raw', 'outperformed', 'quarter_id']]

def apply_partial_dropout(df, k=4):
    if k == 0:
        return df
    return df.groupby('quarter_id').apply(lambda group: group.sample(n=min(k, len(group)))).reset_index(drop=True)

def prepare_model_data(df):
    df = apply_partial_dropout(df, k=0) # Using k=0 as in the original script
    X = df[features].values
    y = df['outperformed'].values
    return X, y

X, y = prepare_model_data(df)
print(X.shape)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

def train_model(model, X_train, y_train, X_test, y_test, model_name):
    """Trains a given model, prints its accuracy, and returns the trained model."""
    print(f"Training {model_name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"{model_name} Test Accuracy: {acc:.4f}")
    return model

# --- Model Training Functions ---

def train_log_reg_l1(X_train, y_train, X_test, y_test):
    # liblinear solver supports L1 penalty
    model = LogisticRegression(penalty='l1', solver='liblinear')
    return train_model(model, X_train, y_train, X_test, y_test, "Logistic Regression (L1)")

def train_log_reg_l2(X_train, y_train, X_test, y_test):
    # liblinear solver supports L1 penalty
    model = LogisticRegression(penalty='l2', solver='liblinear')
    return train_model(model, X_train, y_train, X_test, y_test, "Logistic Regression (L2)")

def train_log_reg_en(X_train, y_train, X_test, y_test):
    model = LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.5, max_iter=1000) # Increased max_iter for saga
    return train_model(model, X_train, y_train, X_test, y_test, "Logistic Regression (ElasticNet)")

def train_lin_svm(X_train, y_train, X_test, y_test):
    model = LinearSVC(random_state=42, dual="auto", C=1.0, max_iter=10000) # Increased max_iter
    return train_model(model, X_train, y_train, X_test, y_test, "Linear SVM")

def train_rbf_svm(X_train, y_train, X_test, y_test):
    # C is the regularization parameter, gamma is the kernel coefficient
    model = SVC(kernel='rbf', C=1.0, gamma='scale')
    return train_model(model, X_train, y_train, X_test, y_test, "RBF SVM")

def train_dt(X_train, y_train, X_test, y_test):
    model = DecisionTreeClassifier(random_state=42)
    return train_model(model, X_train, y_train, X_test, y_test, "Decision Tree")

def train_rf(X_train, y_train, X_test, y_test):
    model = RandomForestClassifier(random_state=42, n_estimators=100) # n_estimators is a common parameter to tune
    return train_model(model, X_train, y_train, X_test, y_test, "Random Forest")

def train_gbm(X_train, y_train, X_test, y_test):
    model = GradientBoostingClassifier(random_state=42, n_estimators=100, learning_rate=0.1) # n_estimators and learning_rate are common
    return train_model(model, X_train, y_train, X_test, y_test, "Gradient Boosted Tree")

# --- Main Training Loop ---
models_to_train = {
    # "log_reg_l1": train_log_reg_l1,
    # "log_reg_en": train_log_reg_en,
    # "lin_svm": train_lin_svm,
    # "rbf_svm": train_rbf_svm,
    "dt": train_dt,
    "rf": train_rf,
    "gbm": train_gbm
}

trained_models = {}

for model_name, training_function in models_to_train.items():
    model = training_function(X_train, y_train, X_test, y_test)
    trained_models[model_name] = model
    model_path = f'models/{model_name}.pkl'
    joblib.dump(model, model_path)
    print(f"Saved {model_name} to {model_path}\n")

print("All models trained and saved.")
