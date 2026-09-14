import warnings


warnings.filterwarnings('ignore')

from rag import ask
BANNER = (
    "╔══════════════════════════════════════════╗\n"
    "║        문서 기반 질의응답 시스템          ║\n"
    "║   종료하려면 'q' 또는 'exit' 입력        ║\n"
    
"╚══════════════════════════════════════════╝" )

def main():
    print(BANNER)
    while True:
        try:
            q = input("\n질문 > ").strip()         
        except (KeyboardInterrupt, EOFError):             
            print("\n종료합니다.")
            break
        if q.lower() in ("q", "exit", "quit", "종료"):             
            print("종료합니다.")
            break
        if not q:
            continue
        result = ask(q)
        print("\n" + "─" * 50)         
        print(result["answer"])         
        
        if result["sources"]:
            print("\n 참고 자료")
            seen = set()
            for s in result["sources"]:
                key = (s["file"], s["page"])
                if key not in seen:
                    seen.add(key)
                    print(f"   · {s['file']} {s['page']}페이지")
                    
        if result.get("cited") is False:             
            print("\n⚠ 인용 표시가 확인되지 않았습니다.")         
            print("─" * 50)
    
if __name__ == "__main__":     
    main()