from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 1. Model ve Araçların Tanımlanması
llm = ChatOpenAI(model="gpt-4o", temperature=0)
tools = [TavilySearchResults(max_results=1)] # Örn: İnternet arama aracı

# 2. Prompt Tasarımı
prompt = ChatPromptTemplate.from_messages([
    ("system", "Sen yardımcı ve profesyonel bir asistansın."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 3. Ajanın Oluşturulması
agent = create_openai_functions_agent(llm, tools, prompt)

# 4. Çalıştırıcı (Executor) Kurulumu
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True,
    handle_parsing_errors=True
)

# 5. Test
response = agent_executor.invoke({"input": "Bugün İstanbul'da hava nasıl?"})
print(response["output"])