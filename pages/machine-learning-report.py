import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# --------------------
# 1) 페이지 & 헤더
# --------------------
st.set_page_config(page_title='Machine Learning Report')
st.sidebar.header('Machine Learning Report')
st.header('Machine Learning Report', divider='rainbow')

# --------------------
# 2) 데이터 로드 & 기본 확인
# --------------------
df = pd.read_csv('Obesity Classification.csv')
st.subheader('Raw Data Preview')
st.write(df.head())

# 결측치 확인
st.subheader('Missing Values')
missing = df.isnull().sum()
st.write(missing)

# 결측치 처리
# 1. BMI나 Age 같은 수치형에 결측이 있으면 평균으로 대체#
num_cols = ['Age','Height','Weight','BMI']
imp_mean = SimpleImputer(strategy='mean')
df[num_cols] = imp_mean.fit_transform(df[num_cols])

# 2. 범주형 결측(성별)에 대해 최빈값 대체
if df['Gender'].isnull().any():
    imp_freq = SimpleImputer(strategy='most_frequent')
    df[['gender']]= imp_freq.fit_transform(df[['Gender']])

# 이상치 처리(IQR)
def cap_outlier(series):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5*IQR
    return series.clip(lower, upper)
for col in num_cols:
    df[col]=cap_outlier(df[col])

# --------------------
# 5) 레이블 인코딩 & 스케일링
# --------------------
le = LabelEncoder()
df['Gender'] = le.fit_transform(df['Gender'])
df['Label_enc'] = le.fit_transform(df['Label'])  # 예측 대상도 인코딩

scaler = StandardScaler()
df[num_cols] = scaler.fit_transform(df[num_cols])

# 불필요 컬럼 제거
df.drop(columns=['ID', 'Label'], inplace=True)

# --------------------
# 6) 특징(독립변수)/타깃(종속변수) 분리 및 분할
# --------------------
X = df.drop('Label_enc', axis=1)
y = df['Label_enc']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
# --------------------
# 7) 하이퍼파라미터 튜닝
#    → RandomizedSearchCV 선택 이유:
#    - 탐색 공간이 크거나 시간 제약이 있을 때 효율적
# --------------------
param_dist = {
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [None, 5, 10, 20],
    'max_features': ['auto', 'sqrt', 'log2'],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}
base_clf = RandomForestClassifier(random_state=42)
rand_search = RandomizedSearchCV(
    estimator=base_clf,
    param_distributions=param_dist,
    n_iter=20,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    random_state=42
)
rand_search.fit(X_train, y_train)
best_clf = rand_search.best_estimator_

# --------------------
# 8) 평가
# --------------------
# 8) 평가 (수정된 부분)
y_pred = best_clf.predict(X_test)

# 8-1) 정확도
acc = accuracy_score(y_test, y_pred)
st.subheader('Model Performance') #비교해야할 예측값
st.write(f'**Accuracy:** {acc:.2f}')

# 8-2) Classification Report → DataFrame → Table
report_dict = classification_report(
    y_test, y_pred,
    target_names=le.classes_,
    output_dict=True
)
report_df = pd.DataFrame(report_dict).T.round(2)
st.subheader('Classification Report')
st.table(report_df)

# 8-3) Confusion Matrix
conf_mat = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(
    conf_mat, annot=True, fmt='d', cmap='YlGnBu',
    xticklabels=le.classes_, yticklabels=le.classes_, ax=ax
)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
ax.set_title('Confusion Matrix')
st.pyplot(fig)
