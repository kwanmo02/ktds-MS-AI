import os
import re
import json
from io import BytesIO
from collections import Counter
import concurrent.futures

import pandas as pd
import networkx as nx
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient

# ----------------------------------------------------------------
# 0. 클러스터 기준 네트워크 시각화 함수
# ----------------------------------------------------------------
def create_cluster_network(results, cluster_list=None, cluster_limit=10, title_limit=10):
    G = nx.Graph()
    title_info_map = {t: r for t, r in results}
    cluster_counts = Counter([r["cluster"] for _, r in results])

    # 1. 클러스터 선정: 직접 리스트 or 빈도 기준 자동 선정
    if cluster_list:
        top_clusters = cluster_list[:cluster_limit]
    else:
        top_clusters = [c for c, _ in cluster_counts.most_common(cluster_limit)]

    for cluster in top_clusters:
        cluster_freq = cluster_counts.get(cluster, 1)
        G.add_node(cluster, node_type="cluster", frequency=cluster_freq)
        titles = [(t, r) for t, r in results if r["cluster"] == cluster][:title_limit]
        for title, r in titles:
            G.add_node(title, node_type="title", frequency=1)
            G.add_edge(cluster, title)
            # 이슈 노드(issue)는 그래프에 추가하지 않음

    # 2. NetworkX 레이아웃 및 시각화
    pos = nx.spring_layout(G, dim=3, seed=42, k=1.0)
    x_edges, y_edges, z_edges = [], [], []
    x_nodes, y_nodes, z_nodes = [], [], []
    for edge in G.edges():
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]
        z_edges += [pos[edge[0]][2], pos[edge[1]][2], None]
    for node in G.nodes():
        x_nodes.append(pos[node][0])
        y_nodes.append(pos[node][1])
        z_nodes.append(pos[node][2])
    node_color, node_size, node_labels, node_hovertexts = [], [], [], []
    def scale_size(freq, base=16, max_scale=60):
        return min(base + freq * 2, max_scale)
    for n in G.nodes():
        t = G.nodes[n].get("node_type", "")
        freq = G.nodes[n].get("frequency", 1)
        # 오직 cluster, title 노드만 시각화
        if t == "cluster":
            color = "#DB1A1A"
            size = scale_size(freq)
            label = n
            hover_text = f"<b>{n}</b><br>유형: {t}<br>VOC 건수: {freq}"
        elif t == "title":
            color = "gainsboro"
            size = 10
            label = ""
            info = title_info_map.get(n)
            hover_text = (
                f"<b>{n}</b><br>유형: {t}<br><br>이슈: {', '.join(info.get('issue', []))}"
                if info else f"{n}"
            )
        else:
            continue  # issue 등 다른 노드는 건너뜀
        node_color.append(color)
        node_size.append(size)
        node_labels.append(label)
        node_hovertexts.append(hover_text)
    fig = go.Figure(data=[
        go.Scatter3d(x=x_edges, y=y_edges, z=z_edges, mode="lines", line=dict(color="lightgray", width=2)),
        go.Scatter3d(
            x=x_nodes, y=y_nodes, z=z_nodes,
            mode="markers+text",
            text=node_labels,
            hovertext=node_hovertexts,
            hovertemplate="%{hovertext}<extra></extra>",
            textposition="top center",
            marker=dict(size=node_size, color=node_color, line=dict(color="black", width=1.2))
        )
    ])
    fig.update_layout(
        title="🧠 클러스터 기준 VOC 네트워크",
        width=1100, height=800,
        scene=dict(xaxis=dict(showbackground=False),
                   yaxis=dict(showbackground=False),
                   zaxis=dict(showbackground=False)),
        margin=dict(l=0, r=0, b=0, t=60)
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------
# 1. 환경설정
# ----------------------------------------------------------------
load_dotenv()
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    azure_endpoint=os.getenv("OPENAI_AZURE_ENDPOINT"),
    api_version=os.getenv("OPENAI_API_VERSION")
)
CHAT_DEPLOYMENT_NAME = os.getenv("CHAT_DEPLOYMENT_NAME")
STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "mvp-voc-data-sample"
FILE_NAME = "서비스문의 목록(샘플2).xls"

# ----------------------------------------------------------------
# 2. 데이터 로딩
# ----------------------------------------------------------------
@st.cache_data(ttl=600)
def load_excel():
    try:
        blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        blob_client = blob_service.get_container_client(CONTAINER_NAME).get_blob_client(FILE_NAME)
        blob_data = blob_client.download_blob().readall()
        return pd.read_excel(BytesIO(blob_data), engine="xlrd")
    except Exception as e:
        st.error(f"📂 엑셀 파일 로딩 실패: {e}")
        return pd.DataFrame()
df = load_excel()
if df.empty:
    st.warning("📭 데이터가 비었습니다.")
    st.stop()

# ----------------------------------------------------------------
# 3. GPT 분석 함수 등 정의
# ----------------------------------------------------------------
sample_prompt = """
아래는 VOC 문의 제목에 대해 키워드, 세부 이슈, 의미적 군집(정규화 클러스터)을 추출하는 예시입니다.
※ 의미적 군집은 아래처럼 동의어·유사표현 이슈끼리 하나의 대표명으로 통일하여 반환해야 합니다.

예시:
문의 제목: "신규가입시 선호번호 조회 안되어 문의"
-> 주요 키워드: 선호번호
-> 세부 이슈: 신규가입 시 선호번호 조회 불가
-> 의미적 군집: 선호번호 조회 실패

문의 제목: "번호변경시 선호번호 선택 오류 발생"
-> 주요 키워드: 선호번호
-> 세부 이슈: 번호 변경 시 선호번호 선택 오류
-> 의미적 군집: 선호번호 조회 실패

문의 제목: "단말 분실 후 유심 이동 불가"
-> 주요 키워드: 유심, 단말기
-> 세부 이슈: 단말기 분실 후 유심 이동이 되지 않음
-> 의미적 군집: 유심/단말 이동 실패

문의 제목: "{title}"
아래의 JSON 형식으로 반환:
{
  "keyword": [...],
  "issue": [...],
  "cluster": "..."  // 반드시 기존 군집과 패턴이 유사하면 동일 명칭 사용!
}
"""
def parse_gpt_response(content: str) -> dict:
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except: pass
    return {"keyword": [], "issue": [], "cluster": "기타"}
def extract_features_gpt(title: str) -> dict:
    prompt = f"{sample_prompt}\n\n문의 제목: \"{title}\"\n\n반환 형식:\n{{\n\"keyword\": [...],\n\"issue\": [...],\n\"cluster\": \"...\"\n}}"
    try:
        response = client.chat.completions.create(
            model=CHAT_DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return parse_gpt_response(response.choices[0].message.content.strip())
    except:
        return {"keyword": [], "issue": [], "cluster": "기타"}
@st.cache_data(ttl=900)
def analyze_titles_parallel(titles):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(extract_features_gpt, t): t for t in titles}
        for future in concurrent.futures.as_completed(futures):
            title = futures[future]
            try:
                result = future.result()
            except:
                result = {"keyword": [], "issue": [], "cluster": "기타"}
            results.append((title, result))
    return results

# ----------------------------------------------------------------
# 4. Streamlit UI/실행부
# ----------------------------------------------------------------
st.title("🧠 VOC Insight 네트워크 분석")

with st.sidebar:
    st.subheader("🔍 키워드 검색")
    col1, col2 = st.columns([4,1])
    with col1:
        search = st.text_input(" ", placeholder="예: 우수기변, 번호이동", label_visibility="collapsed")
    with col2:
        search_btn = st.button("조회")
    sample_size = st.slider("샘플 수", 10, 1000, 100)
    cluster_limit = st.slider("표시할 클러스터 수", 1, 30, 10)
    title_limit = st.slider("클러스터당 제목 수", 1, 20, 5)

# 데이터 필터링
if search_btn:
    df['_cleaned'] = df['문의제목'].str.lower().str.replace(r'\s+', '', regex=True)
    filtered_df = df[df['_cleaned'].str.contains(search.lower().strip())]
else:
    filtered_df = df.sample(n=sample_size) if len(df) > sample_size else df
if filtered_df.empty:
    st.warning("📭 조건에 맞는 VOC가 없습니다.")
    st.stop()


# ----------------------------------------------------------------
# 3. 필터링된 데이터에 한해 GPT 분석 수행
# ----------------------------------------------------------------
with st.spinner("🤖 필터링된 VOC 분석 진행 중..."):
    filtered_analysis_results = analyze_titles_parallel(filtered_df["문의제목"].tolist())

# ----------------------------------------------------------------
# 4. 클러스터 선택 UI & 분기 (최종 추천 구조, session_state 버전)
# ----------------------------------------------------------------

# 1) 필터링된 결과에서 클러스터 옵션 생성
cluster_counts = Counter([r['cluster'] for _, r in filtered_analysis_results])
all_clusters = [c for c, _ in cluster_counts.most_common(50)]  # 옵션 리스트

st.write("📌 all_clusters 옵션:", all_clusters)


# 2) session_state에 선택값이 없으면 초기화
if "selected_clusters" not in st.session_state:
    st.session_state.selected_clusters = []

# 3) 멀티셀렉트 UI 생성 (default를 session_state에서 불러옴)
selected_clusters = st.sidebar.multiselect(
    "클러스터 명 선택 (선택 시 해당 클러스터만 시각화됩니다)",
    options=all_clusters,
    default=st.session_state.selected_clusters,
    key="cluster_multiselect"
)

# 4) 선택한 값 저장
st.session_state.selected_clusters = selected_clusters

# 5) 디버깅 출력 (선택 잘 됐는지 확인용, 필요시 삭제 가능)
st.write("✅ 선택된 클러스터 (session_state):", st.session_state.selected_clusters)

# ----------------------------------------------------------------
# 5. 시각화 (선택 여부에 따른 분기)
# ----------------------------------------------------------------
if selected_clusters:
    cluster_selected = selected_clusters[0]
    st.subheader(f"🎯 선택 클러스터 집중 분석: {cluster_selected}")
    create_cluster_network(filtered_analysis_results, [cluster_selected], cluster_limit=1, title_limit=title_limit)
else:
    st.subheader("📌 필터링된 VOC 기준 상위 클러스터 네트워크")
    create_cluster_network(filtered_analysis_results, None, cluster_limit, title_limit)
