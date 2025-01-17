import os

import pandas as pd
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI  
from langchain.vectorstores import Pinecone  
from langchain.docstore.document import Document  
from langchain.embeddings import OpenAIEmbeddings 
from langchain_pinecone import PineconeVectorStore  
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain_community.chat_message_histories import ChatMessageHistory  

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain

from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


dictSessionHistory = {} # 세션별 채팅 메세지 이력 저장 딕셔너리

# 세션의 채팅 메시지 이력 저장 객체
def CreateSessionHistory(sessionId: str) -> BaseChatMessageHistory:  
    if sessionId not in dictSessionHistory:
        dictSessionHistory[sessionId] = ChatMessageHistory() 
    return dictSessionHistory[sessionId]

# 사용자 질문을 처리하거나 그대로 반환하는 사전 기반 체인 생성 함수
def CreateDictionaryChain(): 
    llm = GetLLM()
    dictionary = []
    
    dictionaryPrompt = ChatPromptTemplate.from_template("""
        사용자의 질문으로 보고, 우리의 사전을 참고해서 사용자의 질문을 변경해주세요.
        만약 변경할 필요가 없다고 판단된다면, 사용자의 질문을 변경하지 않아도 됩니다.
        그런 경우에는 질문만 리턴해주세요.
        
        사전: {dictionary}
                
        질문: {{question}}""")   # 프롬프트 템플릿 -> 사용자 질문을 입력받아 처리 방법을 언어 모델에 지시
    
    dictionaryChain = dictionaryPrompt | llm | StrOutputParser()  # 입력된 질문 템플릿에 삽입 -> 템플릿 처리한 적절한 질문 생성 -> 결과를 문자열로 변환.
    
    return dictionaryChain

# 언어 모델 초기화
def GetLLM(model='gpt-4o'): 
    llm = ChatOpenAI(model=model)
    return llm

# 벡터 검색을 위한 retriever 객체 생성 함수
def CreateRetriever(): 
    embeddingModel = OpenAIEmbeddings(model='text-embedding-3-large')  # OpenAI 임베딩 모델 초기화
    indexName = 'tour-chatbot'  # Pinecone 데이터베이스의 기존 인덱스 연결
    
    vectorDatabase = PineconeVectorStore.from_existing_index(
        index_name=indexName, 
        embedding=embeddingModel)
    
    # 벡터 검색기 생성 (가장 유사한 k개의 결과 반환)
    retriever = vectorDatabase.as_retriever(search_kwargs={'k': 4}) 
    return retriever

# 히스토리 기반 검색기 생성 함수
def CreateHistoryRetriever():
    llm = GetLLM()
    retriever = CreateRetriever()
    
    # 채팅 기록과 사용자의 최신 질문을 바탕으로 질문을 재구성하기 위한 프롬프트 템플릿 생성
    contextualizePrompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Given a chat history and the latest user question "
                       "which might reference context in the chat history, "
                       "formulate a standalone question which can be understood "
                       "without the chat history. Do NOT answer the question, "
                       "just reformulate it if needed and otherwise return it as is."), # 질문 재구성 지시
            MessagesPlaceholder("chat_history"),  # 이전 채팅 기록이 삽입
            ("human", "{input}"),  # 사용자의 최신 질문
        ]
    )  
    
    # 히스토리 기반 검색기 생성
    historyRetriever = create_history_aware_retriever(llm, retriever, contextualizePrompt)  
    return historyRetriever

# RAG(Retrieval-Augmented Generation) 체인 생성하는 함수 
def CreateRagChain():
    llm = GetLLM() 
    
    # 시스템 프롬프트 생성 (사용자 질문 처리 지침)
    systemPrompt = (
        "당신은 관광지 추천해주는 관광사입니다. 사용자의 관광지에 관한 질문에 답변해주세요."
        "아래에 제공된 문서를 활용해서 답변해주시고, "
        "답변을 알 수 없다면 모른다고 답변해주세요. "
        "2-3 문장 정도의 짧은 내용의 답변을 원합니다."
        "\n\n"
        "{context}"
    )
    
    # QA 체인을 위한 프롬프트 생성
    qaPrompt = ChatPromptTemplate.from_messages(
        [
            ("system", systemPrompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    # 히스토리 기반 검색기 생성
    historyRetriever = CreateHistoryRetriever()
    # QA 체인 생성
    qaChain = create_stuff_documents_chain(llm, qaPrompt)
    # 검색-생성 체인 생성
    ragChain = create_retrieval_chain(historyRetriever, qaChain)
    
    # 대화형 RAG 체인 생성
    conversationalRagChain = RunnableWithMessageHistory(
        ragChain,
        CreateSessionHistory,
        input_message_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick('answer')
    
    return conversationalRagChain

# 사용자 메세지를 처리하고 AI 응답을 반환하는 함수
def GetAIResponse(userMessage):
    
    dictionaryChain = CreateDictionaryChain() # 사전 체인 생성 (사용자 질문을 분석 및 변경)
    ragChain = CreateRagChain() # RAG 체인 생성
    finalChain = {"input": dictionaryChain} | ragChain # 사전 체인과 RAG 체인 결합한 최종 처리 체인 생성
    
    aiResponse = finalChain.stream(
        {
            "question": userMessage
        },
        config={
            "configurable": {"session_id": "abc123"}
        },
    )
    
    return aiResponse

