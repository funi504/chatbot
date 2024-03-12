
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document
from langchain_community.llms import GPT4All
import time
from webscrapper import  get_related_data_from_vectordb


#upload_data_to_vectordb('https://www.uj.ac.za')
# create a prompt template where it contains some initial instructions
# here we say our LLM to think step by step and give the answer
def message_reply(user_input , project_id):

    program_start_time = time.time()
    template = """
    you are a helpful assistant who gives short answers

    use this information as context to answer the question : {context},

    extract the information from the text i provided only to answer this question if you know the answer: {input}

    dont use other information if ,  you don't know or not sure about the answer say soo
    """


    prompt = PromptTemplate(template=template, input_variables=["input", "context"])


    local_path = ("./models/orca-mini-3b-gguf2-q4_0.gguf")

    # initialize the LLM and make chain it with the prompts

    llm = GPT4All(
        model=local_path, 
        backend="llama", 
    )

    llm_chain = LLMChain(prompt=prompt, llm=llm, verbose=True)


    model_start_time = time.time()

    #user_input = "tell me about the university of johannesburg"

    #user input and user Id from arguments
    context = get_related_data_from_vectordb( user_input, project_id)
    print(context)
    documents = context.get('documents')

    resp = llm_chain.invoke({
        "input": user_input,
        "context": documents
    })

    resp = resp.get('text','')
    #resp = resp.replace("'", "")
    program_end_time = time.time()

    print(f'response : {resp}')

    print(f'program running time:{program_start_time - program_end_time}')
    print(f'model running time:{model_start_time - program_end_time}')

    return resp