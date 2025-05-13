# 🧭 초보자용 안전 경로 추천 시스템
@injjang  
2025.05 ~ 2025.05

🔗 Live Demo  
https://navibegimd-dhlpdlcvbidv7c9gbprhtj.streamlit.app/

📂 GitHub Repository  
https://github.com/INSEONGBEEN/navi_begimd

📘 Dev Log  
https://lnjjang.tistory.com/

📌 강남구 도로망 데이터를 기반으로, 교차로 위험도를 고려해 초보자에게 더 안전한 경로를 추천하는 시스템입니다.  
Streamlit과 folium 기반 웹 앱으로 구현되었으며, 사용자가 지도에서 출발지와 도착지를 클릭하면  
최단 거리와 위험도 기반 안전 경로를 시각적으로 비교해줍니다.

🛠️ 주요 기능
- 강남구 도로망 자동 수집 및 시각화 (osmnx)
- 교차로의 차선 수, 도로 타입, 신호 유무 등을 기반으로 위험도 산정
- 위험도 기반 가중치를 활용한 안전 경로 탐색
- folium 기반 지도 위에서 출발지/도착지를 직접 클릭하여 경로 계산
- Streamlit Cloud 배포로 웹에서 누구나 접근 가능

🧱 기술 스택

| Category | Tools |
|----------|-------|
| 언어 | Python |
| 도로망 처리 | osmnx, networkx |
| 시각화 | folium, streamlit, streamlit-folium |
| 데이터 처리 | pandas, numpy |
| 배포 환경 | Streamlit Cloud |

🗂️ 디렉토리 구조
📁 navi_begimd  
├── streamlit_safe_route_app.py  
├── requirements.txt  
└── README.md  

🚀 실행 예시
1. 사용자가 강남구 내 지점 두 곳을 클릭
2. 클릭한 지점을 기준으로:
   - 일반 최단 거리 경로 (회색)
   - 초보자 안전 경로 (파랑)
3. 두 경로를 지도 위에 동시에 시각화

🔧 보완할 점 & 향후 아이디어

| 한계점 | 보완 아이디어 |
|--------|----------------|
| 실시간 교통정보 반영 불가 | 공공 API 활용한 실시간 정보 반영 |
| 교차로 위험도 주관적 | 교통사고 이력 등 정량적 데이터 추가 |
| 경로 중단 가능성 | 도보 네트워크 전처리 및 연결성 검사 자동화 |

✍️ 느낀 점
- Streamlit을 통해 지도 기반 인터랙션을 구현하는 데 큰 재미와 실용성을 느낌
- 복잡한 로직을 사용자가 클릭 두 번으로 체험할 수 있는 UX 설계가 인상 깊었음
- 데이터 시각화보다 실제 경로 추천으로 연결될 때 전달력이 훨씬 높아짐
