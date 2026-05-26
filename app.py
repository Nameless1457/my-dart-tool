import streamlit as st
import OpenDartReader
import pandas as pd

st.set_page_config(page_title="세아제강 공시 분석", layout="wide")
st.title("📈 세아제강 vs 경쟁사 분석 대시보드")

# 사이드바 설정
st.sidebar.header("⚙️ 설정")
year = st.sidebar.selectbox("분석 연도", ["2023", "2022", "2021"])

# 메인 화면 - 경쟁사 입력
target_company = st.text_input("비교할 경쟁사 이름을 입력하세요 (예: 현대제철, 휴스틸)", "현대제철")

# 외부 비밀 금고(Secrets)에서 키를 안전하게 가져오기
try:
    raw_key = st.secrets["DART_API_KEY"]
    
    # [방탄 조치] 혹시라도 묻어왔을지 모르는 앞뒤 공백, 큰따옴표, 작은따옴표를 완벽히 제거하고 순수 글자로 변환합니다.
    api_key = str(raw_key).strip().strip('"').strip("'")
    
except KeyError:
    st.error("🔒 Streamlit Cloud 설정에서 'DART_API_KEY'를 등록해 주세요!")
    st.stop()

if api_key:
    try:
        # 안전하게 DART 연결 기동
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
        st.error(f"⚠️ DART 시스템과 연결 중 문제가 발생했습니다. 조금 뒤에 다시 시도해 주세요. (에러 내용: {e})")
else:
    st.warning("API 키가 올바르지 않습니다.")
