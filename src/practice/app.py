from rag import ask

BANNER = (
    "\n"
    "==================================================\n"
    "          새봄도서관 이용 안내 챗봇\n"
    "==================================================\n"
    "예시: 책은 몇 권까지 빌릴 수 있나요?\n"
    "예시: 다른 사람이 예약한 책도 연장할 수 있나요?\n"
    "종료: q / exit / quit / 종료\n"
)


def main():
    print(BANNER)

    while True:
        try:
            question = input("\n질문 > ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\n종료합니다.")
            break

        if question.lower() in ("q", "exit", "quit", "종료"):
            print("종료합니다.")
            break

        if not question:
            print("질문을 입력해주세요.")
            continue

        result = ask(question)

        print("\n" + "─" * 50)
        print(result["answer"])

        if result["sources"]:
            print("\n출처")

            for source in result["sources"]:
                print(
                    f"  [{source['number']}] "
                    f"{source['file']} · "
                    f"{source['page']}페이지"
                )

        print("─" * 50)


if __name__ == "__main__":
    main()