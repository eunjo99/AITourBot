import streamlit as st

# 페이지 설정
def SetupPage():
    st.set_page_config(page_title="관광지 추천 챗봇", page_icon="🤖")

# 초기 UI 설정
def RenderUI():
    st.title("관광지 추천 챗봇")
    st.caption("원하는 지역을 말씀해 주시면 관광지를 추천해드릴게요!!")

# 세션 상태 초기화
def InitializeMessageList():
    if 'listMessage' not in st.session_state:
        st.session_state.listMessage = []

# 이전 메시지 표시
def DisplayMessageHistory():
    for dictMessage in st.session_state.listMessage:
        with st.chat_message(dictMessage["role"]):
            st.write(dictMessage["content"])

# 사용자 입력 처리
def ProcessUserInput():
    strUserQuestion = st.chat_input(placeholder="원하는 지역을 말씀해 주시면 관광지를 추천해드릴게요!")
    if strUserQuestion:
        with st.chat_message("user"):
            st.write(strUserQuestion)
        st.session_state.listMessage.append({"role": "user", "content": strUserQuestion})
        
        # AI 응답 처리 (추후 AI 로직 연동 가능)
        with st.chat_message("ai"):
            strAIResponse = "여기는 AI 메세지가 올 예정"
            st.write(strAIResponse)
        st.session_state.listMessage.append({"role": "ai", "content": strAIResponse})

# 메인 함수
def Main():
    SetupPage()
    RenderUI()
    InitializeMessageList()
    DisplayMessageHistory()
    ProcessUserInput()

if __name__ == "__main__":
    Main()
    
