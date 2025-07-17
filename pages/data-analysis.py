import streamlit as st
import pandas as pd
import plotly

# 파일 읽기 (확장자 포함!)
df = pd.read_csv('Obesity Classification.csv')

# 페이지 설정
st.set_page_config(page_title='데이터분석')

# 사이드바
st.sidebar.header('비만도 데이터 분석')

# 마크다운 정보 출력
st.markdown('''
### 📊 비만도 데이터 설명

- **Age**: 나이  
- **Gender**: 성별  
- **Height**: 키  
- **Weight**: 몸무게  
- **BMI**: 체질량지수  
- **Label**: 각 개인의 비만 여부
''')

t1, t2, t3, t4 = st.tabs(['상위데이터', '데이터 통계', '컬럼데이터', '조건데이터'])
with t1:
    dh=df.head(20)
    st.write(dh)
with t2:
    dd=df.describe()
    st.write(dd)    
with t3:
    col=df.columns.tolist()
    col=col[0:]
    se_col=st.multiselect('select col',col)  #말그대로 멀티(다시 드랍해서 다른 버튼 누르면 멀티로 셀렉 되는 것)
    new_df = df.loc[:,se_col]
    st.write(new_df)

with t4:
    c=st.selectbox('**select Label**',('Normal Weight', 'OverWeight', 'UnderWeight'))
    c_df = df.loc[df['Label'] == c]    
    st.write(c_df)
            

