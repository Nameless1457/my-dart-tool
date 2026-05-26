import streamlit as st
import OpenDartReader
import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 설정 (웹 서버 환경을 고려하여 설정)
plt.rc('font', family='NanumGothic') 

st.title("📈 세아제강 vs 경쟁사 분석 대시보드")

# 1. 사이드바 - API 키 및 설정
st.sidebar.header("설정")
api_key = st.sidebar.text_input("0519ee928ccb3b99dad9980f566af24b62a4273b", type="password")
year = st.sidebar.selectbox("분석 연도", ["2023", "2022", "2021"])

# 2. 메인 화면 - 경쟁사 입력
target_company = st.text_input("비교할 경쟁사 이름을 입력하세요 (예: 현대제철, 휴스틸)", "현대제철")

if api_key:
    dart = OpenDartReader(api_key)
    
    # 세아제강 정보 (고정)
    seah_code = '00306200' # 세아제강 corp_code
    
    try:
        # 데이터 가져오는 함수
        def get_finance_data(corp_name, corp_code):
            df = dart.finstate(corp_code, year) # 재무제표 가져오기
            # 매출액과 영업이익만 추출
            rev = df[df['account_nm'] == '매출액']['thstrm_amount'].values[0]
            op = df[df['account_nm'] == '영업이익']['thstrm_amount'].values[0]
            return int(rev), int(op)

        # 자사 및 타사 데이터 수집
        seah_rev, seah_op = get_finance_data("세아제강", seah_code)
        comp_rev, comp_op = get_finance_data(target_company, target_company)

        # 데이터 프레임 만들기
        data = {
            '항목': ['매출액', '영업이익'],
            '세아제강': [seah_rev, seah_op],
            target_company: [comp_rev, comp_op]
        }
        df_display = pd.DataFrame(data)

        # 3. 결과 화면 출력
        st.subheader(f"📊 {year}년도 실적 비교 (단위: 원)")
        st.table(df_display.style.format(subset=['세아제강', target_company], formatter="{:,}"))

        # 시각화 (막대 그래프)
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### 매출액 비교")
            st.bar_chart(df_display.set_index('항목').loc['매출액'])

        with col2:
            st.write("### 영업이익 비교")
            st.bar_chart(df_display.set_index('항목').loc['영업이익'])

        # 인사이트 자동 생성 (예시)
        op_margin_seah = (seah_op / seah_rev) * 100
        op_margin_comp = (comp_op / comp_rev) * 100
        
        st.info(f"💡 **분석 결과:** 세아제강의 영업이익률은 **{op_margin_seah:.1f}%**이며, "
                f"{target_company}의 영업이익률은 **{op_margin_comp:.1f}%**입니다.")

    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다. 회사 이름을 정확히 입력했는지, API 키가 맞는지 확인해 주세요. (에러: {e})")
else:
    st.warning("왼쪽 사이드바에 DART API 키를 입력해 주세요.")
