import streamlit as st
from langchain_community.vectorstores import FAISS
from typing import Any, Dict, Optional, List
from utils.config import get_embeddings
from retrieval.search_service import get_search_content, improve_search_query


# st.cache_resource 데코레이터를 사용하여 벡터 스토어를 캐싱
@st.cache_resource(show_spinner="문서 검색 중...")
def get_topic_vector_store(
    topic: str, role: str, language: str = "ko"
) -> Optional[FAISS]:

    # 검색어 생성
    improved_queries = improve_search_query(topic, role)
    # 개선된 검색어로 검색 콘텐츠 가져오기
    documents = get_search_content(improved_queries, language)
    if not documents:
        return None
    try:
        return FAISS.from_documents(documents, get_embeddings())
    except Exception as e:
        st.error(f"Vector DB 생성 중 오류 발생: {str(e)}")
        return None


"""
검색 과정은
1. 주제와 역할을 입력으로 받아서 검색어를 생성
2. 개선된 검색어로 검색 콘텐츠 가져오기
3. 가져온 콘텐츠로 벡터 스토어 생성
4. 벡터 스토어에서 Similarity Search 수행
5. 결과 반환
"""


def search_topic(topic: str, role: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
    # 문서를 검색해서 벡터 스토어 생성
    vector_store = get_topic_vector_store(topic, role)
    if not vector_store:
        return []
    try:
        # 벡터 스토어에서 Similarity Search 수행
        return vector_store.similarity_search(query, k=k)
    except Exception as e:
        st.error(f"검색 중 오류 발생: {str(e)}")
        return []
