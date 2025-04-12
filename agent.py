from nearai.agents.environment import Environment

def run(env: Environment):
    system_prompt = {
        "role": "system",
        "content": """You are a code analysis agent that examines code for TODOs and incomplete functions.
        
        When analyzing code, you should:
        1. Look for any comments containing "TODO" and report their line numbers and content
        2. Identify incomplete functions, which include:
           - Empty functions
           - Functions that only contain 'pass'
           - Functions that only have a docstring
        3. Format your response in a clear way with:
           - A section for TODO comments found
           - A section for incomplete functions found
           - Use emojis and clear formatting to make the results readable
        
        If no code is shared, ask the user to share code within triple backticks (```).
        If no TODOs or incomplete functions are found, mention that the code looks complete.
        """
    }
    
    messages = env.list_messages()
    if not messages:
        env.add_reply("Hello! I'm your code analysis assistant. Share some code with me, and I'll check for TODOs and incomplete functions!")
    else:
        result = env.completion([system_prompt] + env.list_messages())
        env.add_reply(result)
    
    env.request_user_input()

run(env)

