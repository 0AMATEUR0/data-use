from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from tools.service import DATAFRAME_REGISTRY
from agent import Agent
from dotenv import load_dotenv

load_dotenv()




def main(query: str = None, file_path: str = None):
    try:
        llm=ChatDeepSeek(model='deepseek-chat', temperature=0.0, max_tokens=8192)
        # llm=ChatOpenAI(model='gpt-4o', temperature=0.0)
        agent = Agent(llm=llm, max_steps=100, max_memory=10, file_path=file_path)
        agent.print_response(query)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_path = "D:/Project/SAPagent/SAP-data/ACC_Short_barge"
    query = """
            1. 从文件 "2024年6月DLD-drayage transport.xlsx" 中读取 AC 列的不含税金额（最后一个非空数据行是总计行，不需要考虑），每一条金额将生成两行会计数据（借方和贷方）。
            2. 读取文件 "4.Accrual Short barge fee-Template.xlsx"，然后将获取的不含税金额写入此文件，写入规则如下：
                - A列固定为 5531；
                - B列一行写 DR，一行写 CR；
                - C列：DR 行为 60900000，CR 行为 38610000；
                - E列写入原始不含税金额；
                - F列：对于C列为 38610000 的行，其对应的B列若是CR， 则写 09，否则写 08；C列为 60900000 的行直接为空。
                - H列：若 C 为 60900000，则写 "Cost Center"；若为 38610000，则写 "Profit Center"；
                - I列：若 C 为 60900000，则写 "72MSCO"；若为 38610000，则写 "P72MSCO"；
                - N列和 O列填写凭证描述：“Acc short barge YYYYMM”，其中 YYYYMM 从文件名中提取（例如“202406”来自“2024年6月”）；
                - 每条金额写两行，一行借方一行贷方。（最后一行是总计行，不需要考虑）
            3. 将你注册的Tabelle1对象写回excel文件中并储存。
            """
    
    main(query=query, file_path=file_path)
    #  2. 简单复合数据，不含税金额=单价(W列)*数量(X列)+其他费用(Z列)。运费(Y列)=单价(W列)*数量(X列)