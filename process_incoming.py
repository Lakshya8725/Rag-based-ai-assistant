"""
Step 5 of the RAG pipeline: answer user questions about the course (CLI).
"""

from rag_engine import ask_question


def main() -> None:
    query = input("Ask a question: ")
    result = ask_question(query)

    print("\n--- ANSWER ---\n")
    print(result["answer"])

    if result["sources"]:
        print("\n--- SOURCES ---")
        for src in result["sources"]:
            print(
                f"  Video {src['video_number']} | {src['start']}-{src['end']} | "
                f"{src['title']} (score: {src['score']})"
            )


if __name__ == "__main__":
    main()
