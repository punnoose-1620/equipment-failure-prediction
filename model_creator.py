import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
import joblib

def train_logistic_regression(X_train, y_train):
    model = LogisticRegression(max_iter=1000, verbose=1)
    model.fit(X_train, y_train)
    joblib.dump(model, 'logistic_regression_model.joblib')
    print("Logistic Regression model saved.")

def train_decision_tree(X_train, y_train):
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, 'decision_tree_model.joblib')
    print("Decision Tree model saved.")

def train_random_forest(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, 'random_forest_model.joblib')
    print("Random Forest model saved.")

def train_svm(X_train, y_train):
    model = SVC(probability=True)
    model.fit(X_train, y_train)
    joblib.dump(model, 'svm_model.joblib')
    print("SVM model saved.")

def train_knn(X_train, y_train):
    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train, y_train)
    joblib.dump(model, 'knn_model.joblib')
    print("KNN model saved.")

def train_neural_network(X_train, y_train):
    model = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, 'neural_network_model.joblib')
    print("Neural Network model saved.")

# train_logistic_regression(X_train, y_train)
# train_decision_tree(X_train, y_train)
# train_random_forest(X_train, y_train)
# train_svm(X_train, y_train)
# train_knn(X_train, y_train)
# train_neural_network(X_train, y_train)
