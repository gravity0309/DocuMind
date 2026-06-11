from rag import build_qa_chain

chain = build_qa_chain("your_test.pdf")  # drop any PDF in /backend
answer = chain.invoke("What is this document about?")
print(answer)