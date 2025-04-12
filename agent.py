from nearai.agents.environment import Environment
import re
import ast


def analyze_code(code: str) -> dict:
    """
    Analyze code for TODOs and potentially incomplete functions.
    Returns a dictionary with analysis results.
    """
    results = {
        'todos': [],
        'incomplete_functions': []
    }
    
    # Find TODO comments
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        if 'TODO' in line:
            results['todos'].append({
                'line': i,
                'content': line.strip()
            })
    
    # Parse code to find potentially incomplete functions
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for empty functions or functions with only pass statement
                if (len(node.body) == 0 or 
                    (len(node.body) == 1 and isinstance(node.body[0], ast.Pass))):
                    results['incomplete_functions'].append({
                        'name': node.name,
                        'line': node.lineno
                    })
                # Check for functions with only docstring
                elif (len(node.body) == 1 and 
                      isinstance(node.body[0], ast.Expr) and 
                      isinstance(node.body[0].value, ast.Str)):
                    results['incomplete_functions'].append({
                        'name': node.name,
                        'line': node.lineno
                    })
    except SyntaxError:
        # If code can't be parsed, we'll skip the incomplete function analysis
        pass
    
    return results


def format_analysis_results(results: dict) -> str:
    """Format the analysis results into a readable message."""
    message = "Code Analysis Results:\n\n"
    
    if results['todos']:
        message += "📝 TODO Comments Found:\n"
        for todo in results['todos']:
            message += f"- Line {todo['line']}: {todo['content']}\n"
    else:
        message += "✅ No TODO comments found.\n"
    
    if results['incomplete_functions']:
        message += "\n🔍 Potentially Incomplete Functions:\n"
        for func in results['incomplete_functions']:
            message += f"- {func['name']} (Line {func['line']})\n"
    else:
        message += "\n✅ No incomplete functions detected.\n"
    
    return message


def run(env: Environment):
    # Set up the system prompt
    system_prompt = {
        "role": "system",
        "content": """You are a code analysis agent that examines code for TODOs and incomplete functions. 
        When users share code with you, analyze it and provide helpful feedback about any TODOs or 
        incomplete implementations you find."""
    }
    
    messages = env.list_messages()
    if not messages:
        # Initial greeting
        env.add_reply("Hello! I'm your code analysis assistant. Share some code with me, and I'll check for TODOs and incomplete functions!")
        env.request_user_input()
        return
    
    # Try to extract code blocks from the last message
    last_message = messages[-1]['content']
    code_blocks = re.findall(r'```(?:[\w]*\n)?(.*?)```', last_message, re.DOTALL)
    
    if not code_blocks:
        env.add_reply("I don't see any code to analyze. Please share your code within triple backticks (```)")
        env.request_user_input()
        return
    
    # Analyze each code block
    for code in code_blocks:
        results = analyze_code(code)
        analysis_message = format_analysis_results(results)
        env.add_reply(analysis_message)
    
    env.request_user_input()

run(env)

