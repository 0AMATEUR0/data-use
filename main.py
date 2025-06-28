from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from agent import Agent
from dotenv import load_dotenv
load_dotenv()
def main():
    llm=ChatDeepSeek(model='deepseek-chat', temperature=0.0, max_tokens=16384)
    agent = Agent(llm=llm, file_path="D:/Project/SAPagent/SAP-data/ACC_Short_barge")
    query=input("Enter your query: ")
    agent.print_response(query)

if __name__ == "__main__":
    main()