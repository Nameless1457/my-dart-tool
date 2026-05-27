import streamlit as st
import OpenDartReader
import pandas as pd
import os

st.set_page_config(page_title="세아제강 공시 분석", layout="wide")
st.title("📈 세아제강 vs 경쟁사 분석 대시보드")

# 사이드바 설정
st.sidebar.header("⚙️ 설정")
year = st.sidebar.selectbox("분석 연도", ["2023", "2022", "2021"])

# 메인 화면 - 경쟁사 입력
target_company = st.text_input("비교할 경쟁사 이름을 입력하세요 (예: 현대제철, 휴스틸)", "현대제철")

# [⚠️ 핵심 수정] st.secrets 관련 코드를 단 한 줄도 남기지 않고 모두 지웠습니다.
# 오직 클라우드타입 전용 시스템 금고(os.environ)만 확인합니다.
api_key = os.environ.get("DART_API_KEY")

if api_key:
    # 혹시라도 묻어왔을지 모르는 공백이나 따옴표 제거
    api_key = str(api_key).strip().strip('"').strip("'")
else:
    st.error("🔒 클라우드타입 설정창에서 '환경 변수(DART_API_KEY)'를 등록해 주세요!")
    st.stop()

if api_key:
    try:
        dart = OpenDartReader(api_key)
        seah_code = '00306200' 
        
        def get_finance_data(corp_identifier):
            df = dart.finstate(corp_identifier, year)
            if df is None or df.empty:
                return None, None
                
            rev_row = df[df['account_nm'].isin(['매출액', '수익(매출액)', '영업수익'])]
            op_row = df[df['account_nm'].isin(['영업이익', '영업손익', '영업이익(손실)'])]
            
            if rev_row.empty or op_row.empty:
                return None, None
                
            rev = int(rev_row['thstrm_amount'].values[0])
            op = int(op_row['thstrm_amount'].values[0])
            return rev, op

        # 데이터 수집 및 화면 표시
        seah_rev, seah_op = get_finance_data(seah_code)
        comp_rev, comp_op = get_finance_data(target_company)

        if seah_rev and comp_rev:
            data = {
                '항목': ['매출액', '영업이익'],
                '세아제강': [seah_rev, seah_op],
                target_company: [comp_rev, comp_op]
            }
            df_display = pd.DataFrame(data).set_index('항목')

            st.subheader(f"📊 {year}년도 실적 비교")
            st.table(df_display.style.format("{:,} 원"))

            col1, col2 = st.columns(2)
            with col1:
                st.write("### 💰 매출액 비교")
                st.bar_chart(df_display.loc['매출액'])
            with col2:
                st.write("### 📉 영업이익 비교")
                st.bar_chart(df_display.loc['영업이익'])

            op_margin_seah = (seah_op / seah_rev) * 100
            op_margin_comp = (comp_op / comp_rev) * 100
            
            st.info(f"💡 **분석 결과:** 세아제강의 영업이익률은 **{op_margin_seah:.1f}%**이며, "
                    f"{target_company}의 영업이익률은 **{op_margin_comp:.1f}%**입니다.")
        else:
            st.error("회사 정보를 찾을 수 없거나 해당 연도의 표준재무제표가 공시되지 않았습니다.")

    except Exception as e:
        st.error(f"⚠️ 데이터 처리 중 문제가 발생했습니다. (에러 내용: {e})")
