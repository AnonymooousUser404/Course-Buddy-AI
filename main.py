import os
from rapidfuzz import fuzz
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough, RunnableSequence, history
from langchain_huggingface import HuggingFaceEmbeddings

from handle_department_lingos import handle_department_lingo


# This line loads the variables from your .env file into the environment
load_dotenv()

# You can now access your key using os.getenv()
my_api_key = os.getenv("GOOGLE_API_KEY")

# You can verify it's loaded (optional)
if my_api_key:
    print("✅ API Key loaded successfully!")
else:
    print("❌ Could not load API Key. Check your .env file and path.")


embedding_model = HuggingFaceEmbeddings(
    model_name = 'sentence-transformers/all-MiniLM-L6-v2'
)

vector_store = Chroma(
    embedding_function = embedding_model,
    persist_directory='course_vector_database',
    collection_name = 'sample'
)


def courses_by_topics(search_filter, descriptive_query):
    if len(search_filter) == 1:
        filter_arg = search_filter
    else:
        filter_arg = {'$and': [{k:v} for k,v in search_filter.items()]}

    retriever = vector_store.as_retriever(search_kwargs={"filter": filter_arg, "k": 100})
    filtered_docs = retriever.get_relevant_documents("")

    filtered_ids = list(set([doc.metadata.get("index") for doc in filtered_docs]))

    filtered_ids = [id_ for id_ in filtered_ids if id_ is not None]

    if filtered_ids:
        id_filter = {"index": {"$in": filtered_ids}}
        print(id_filter)
        # Now do semantic search within these filtered docs
        semantic_retriever = vector_store.as_retriever(
            search_kwargs={"filter": id_filter, "k": 5}
        )
        # Use the descriptive_query for semantic search
        retrieved_docs = semantic_retriever.get_relevant_documents(descriptive_query)
    else:
        print("No valid IDs found in filtered docs for semantic search.")
        retrieved_docs = []
    return retrieved_docs

def instructor_fuzzy_match(doc_instructors, search_instructors):

    # Both are lists of instructor names (strings)
    for search_name in search_instructors:
        for doc_name in doc_instructors:
            if fuzz.token_sort_ratio(doc_name.lower(), search_name.lower()) >= 80:
                return True
    return False

gemini_router_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
gemini_generator_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0) 

history_aware_prompt = ChatPromptTemplate.from_messages([
    ("system", """Your task is to rephrase a follow-up user question into a self-contained, standalone question based on the provided chat history.

    **CRITICAL RULE: Do NOT answer the user's question. Your ONLY job is to reformulate the question itself.**

    Here is an example:

    <Chat History>
    Human: "what is the course content of CS 772"
    AI: "CS 772 covers topics like dynamic programming, graph algorithms, and NP-completeness."
    </Chat History>

    <User Question>
    "Any course similar to that one?"
    </User Question>

    <Standalone Question>
    "Are there any courses similar to CS 772?"
    </Standalone Question>

    If the user's question is already standalone, return it unchanged.
    """),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

class CourseMetadataSearch(BaseModel):
    """A tool to find courses using filters like instructor, course code, slot, or department."""
    course_code: str = Field(default=None, description="The code for the course, e.g., 'bb706'")
    instructors: str = Field(default=None, description="The name of the instructor")
    slot: str = Field(default=None, description="The schedule slot for the course, e.g., '6'")
    department: str = Field(default=None, description="The department offering the course, e.g., 'Physics', 'Mathematics', or 'Bioscience and Engineering'")
    user_intent: str = Field(default=None, description='Tells us if the user wants courses similar to some course, a general enquiry of some course, or is just chatting. Should be one of "get_course_detail", "similar_courses", "courses_by_topics", or "chatting".')
    descriptive_query: str = Field(default=None, description = "The enhanced user query for better semantic search, containing only the topics to be taught in the course.")

    def __init__(self, **data):
        super().__init__(**data)
        # Standardize fields to lowercase for consistent filtering
        if self.course_code is not None:
            self.course_code = self.course_code.lower().replace(" ", "").replace("-", "")
        if self.instructors is not None:
            self.instructors = self.instructors.lower()
        if self.slot is not None:
            self.slot = self.slot.lower()
        if self.department is not None:
            self.department = self.department.lower()

router_prompt = ChatPromptTemplate.from_messages([
    ("system", """Analyze the user's query to determine whether they are asking for specific course details based on course code, professor, or slot. 
    If a specific course is identified, extract the relevant details. 
    Identify and extract:
    - Instructor name (e.g. prof. ramesh chandra -> ramesh chandra)
    - Course code (e.g. BB-706, bb 706, Bb 706 or bb   706 to bb706 i.e. to lowercase and no gap between characters and numbers)
    - Department (If the query contains a department mention (full name, slang, or abbreviation), return it **exactly as written** by the user just remove the "department", "dept" or similar keywords from it. )
    - Slot number 
    - user intent (Tells us if the user is seeking similar courses, wants to query about some course, or wants to know about the chatbot -> "get_course_detail", "similar_courses", "courses_by_topics" or "chatting")
    - descriptive query (contains only the topics to be taught in course.)
    """),
    ("human", "{query}")
])

final_prompt_template = """
    You are a helpful college course assistant named Course Buddy AI, assisting students with course-related questions and helping them find courses of interest. Answer the user's question based ONLY on the following context and chat history.

    If the context is empty:
    - First, check the chat history (HISTORY below). If you find any previous conversation or information in the chat history that is relevant to the user's current question, use it to answer appropriately.
    - If nothing relevant is found in the chat history:
        - If the user's query is about a course (e.g., asking for course details, information, or recommendations), apologize and state that you couldn't find information on that specific topic.
        - If the user's query is general chatting (not about a course), respond appropriately as a friendly assistant (e.g., introduce yourself, offer help, or answer the chatty question).

    HISTORY:
    {chat_history}

    CONTEXT:
    {context}

    QUESTION:
    {question}

    YOUR ANSWER:
    """

chat_history = []

llm_with_tool = gemini_router_llm.with_structured_output(CourseMetadataSearch)

final_prompt = ChatPromptTemplate.from_template(final_prompt_template)

pre_retrieval_router_chain = RunnableSequence(router_prompt,llm_with_tool)
final_rag_chain = RunnableSequence(final_prompt,gemini_generator_llm,StrOutputParser())

query_rewriter_runnable = RunnableSequence(history_aware_prompt,gemini_router_llm,StrOutputParser())

def get_course_detail(search_filter):
    print(f"➡️ Router Decision: METADATA filtering. Filter: {search_filter}")

    # Remove 'user_intent' from filter
    search_filter.pop('user_intent', None)
    search_filter.pop('descriptive_query',None)

    instructors = None
    if "instructors" in search_filter:
        instructors = search_filter['instructors']
        del search_filter['instructors']

    # Defensive: If search_filter is empty or None, use empty dict
    if not search_filter:
        filter_arg = {}
    elif len(search_filter) == 1:
        filter_arg = search_filter
    else:
        # Only use $and if there are at least two filters
        filter_arg = {"$and": [{k: v} for k, v in search_filter.items()]}

    if(search_filter):
        retriever = vector_store.as_retriever(search_kwargs={"filter": filter_arg, "k": 50})
    else:
        retriever = vector_store.as_retriever(search_kwargs={"k": 50})
        
    docs = retriever.get_relevant_documents("")

    if instructors:
        retrieved_docs = [doc for doc in docs if "instructors" in doc.metadata and instructor_fuzzy_match(doc.metadata["instructors"], instructors)]
    else:
        retrieved_docs = docs[:10]
    
    return retrieved_docs

def similar_courses(search_filter):
    print(f"➡️ Router Decision: METADATA + SEMANTIC search. (SIMILAR COURSES). Filter: {search_filter}")

    del search_filter["user_intent"]
    search_filter.pop('descriptive_query',None)

    if not search_filter:
        retrieved_docs = []
    else:
        retriever = vector_store.as_retriever(search_kwargs = {'filter': search_filter, "k" : 1})
        docs = retriever.get_relevant_documents("")
        
        if docs:
            descriptive_query = docs[0].page_content
            # We can also get the index of the doc and combine the page_content of all the results give it to llm to generate summary of that and then do the semantic search
            retriever = vector_store.as_retriever()
            retrieved_docs = retriever.get_relevant_documents(descriptive_query)
        else:
            retrieved_docs = []
    
    return retrieved_docs

def courses_by_topics_router(search_filter):
    search_filter.pop("user_intent", None)
    descriptive_query = search_filter.pop("descriptive_query", None)

    if descriptive_query is None:
        print("❌ Error: Please provide some more information about the course.")
        return []

    if search_filter:
        print(f"➡️ Router Decision: METADATA + SEMANTIC search. (COURSES BY TOPICS). Filter: {search_filter}")
        retrieved_docs = courses_by_topics(search_filter, descriptive_query) 
    else:
        print(f"➡️ Router Decision: Semantic search. Filter: {search_filter}")
        retriever = vector_store.as_retriever()
        retrieved_docs = retriever.get_relevant_documents(descriptive_query)
    
    return retrieved_docs


while(True):
    query = input("🌟 What would you like to ask Course Buddy AI today? (Type your question below) \n> ")

    if(query == "exit"):
        exit()
    query = query_rewriter_runnable.invoke({"chat_history":chat_history,"question":query})
    router_decision = pre_retrieval_router_chain.invoke({"query": query})
    search_filter = {key: value for key, value in router_decision.dict().items() if value is not None}
    search_filter,query = handle_department_lingo(search_filter,query)

    print(f"⚙️ Search Filter: {search_filter}")


    search_chain = RunnableBranch(
    (lambda d: d.get("user_intent") == "get_course_detail",
    RunnableLambda(get_course_detail)),

    (lambda d: d.get("user_intent") == "similar_courses",
    RunnableLambda(similar_courses)),

    (lambda d: d.get("user_intent") == "courses_by_topics",
    RunnableLambda(courses_by_topics_router)),

    RunnablePassthrough()
    )

    context = search_chain.invoke(search_filter)  # pass dict directly



    answer = final_rag_chain.invoke({
        "context": context,
        "question": query,
        "chat_history" : chat_history 
    })

    chat_history.append(HumanMessage(query))  
    chat_history.append(AIMessage(answer)) 
    
    print("🎓 Course Buddy AI :\n",answer)


