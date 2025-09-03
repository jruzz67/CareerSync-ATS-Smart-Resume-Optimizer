from util import setup_logging, configure_gemini

# Setup logging
logger = setup_logging()

# Configure Gemini
genai = configure_gemini()

def initialize_chatbot(vectorstore, job_title):
    if vectorstore is None:
        logger.error("Vectorstore is None")
        raise ValueError("Valid vectorstore is required")
    
    def chatbot(query):
        if not query:
            logger.error("Query is empty")
            raise ValueError("Query is required")
        
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.get_relevant_documents(query)
        context = "\n".join([doc.page_content for doc in docs])

        prompt = f"""
        You are an expert resume advisor for a {job_title} role.
        Use the following context from the resume and ATS analysis to answer the query.
        
        Context: {context}
        
        Query: {query}
        
        Keep responses concise, ATS-optimized, and highly role-specific.
        """

        try:
            # Initialize Gemini model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 500,
                    "temperature": 0.5
                }
            )
            result = response.text.strip()
            logger.debug(f"Chatbot response: {result[:100]}...")
            return result
        except Exception as e:
            logger.error(f"Chatbot response error: {str(e)}")
            raise RuntimeError(f"Failed to get chatbot response: {str(e)}")

    return chatbot