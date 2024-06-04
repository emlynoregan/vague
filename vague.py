'''
This module provides two functions:

- answer(question): response
  A simple function to take a question and return an answer. It is resolved by an excellent LLM,
  and can be used to make judgements, answer questions, or provide information.
- vague(instructions, **kwargs): response
  A function that takes a set of instructions, and attempts to turn those instructions into a python function.
  It uses an LLM to generate the function based on the instructions, and includes access to locals and 
  globals in generating the function. It returns the result of the function. The general approach is:
   - If a function has already been generated for the instructions, call it and return the result.
    - Otherwise, generate a prompt including the instructions, and information about the locals and globals,
     and ask a code generating LLM to generate a function. Cache the function for later, call it, and return the result.
'''
import openai
import json
import inspect
import base64
import types

def get_client():
    # if openai.json doesn't exist, create it and write a template.
    try:
        with open("openai.json") as f:
            openaicreds = json.load(f)

        return openai.OpenAI(api_key=openaicreds.get("api_key"))
    except FileNotFoundError:
        with open("openai.json", "w") as f:
            json.dump({"api_key": "your-api-key"}, f)
        raise Exception("Please add your OpenAI API key to the openai.json file.")


def answer(question, client=None):
    '''
    A simple function to take a prompt and return a response. It is resolved by an excellent LLM,
    and can be used to make judgements, answer questions, or provide information.
    '''
    MODEL="gpt-4o"

    client = client or get_client()

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an intelligent assistant. Answer the user's question."},
            {"role": "user", "content": question}
        ]
    )

    return completion.choices[0].message.content

C_VAGUE_FUNCTIONS = None

def hash_instructions(instructions, **kwargs):
    # use sha-1 to hash the instructions and kwargs, and return the hash.
    import hashlib
    hash_object = hashlib.sha1(f"{instructions}{kwargs}".encode())
    return hash_object.hexdigest()

C_FUNCTION_CODES = {}

# def save_vague_functions():
#     print ("Saving vague functions...")
#     # save the cache of functions to a file.

#     # we need to pull out all the pieces of the functions, and store them in a way that can be serialized.

#     global C_VAGUE_FUNCTIONS
#     serialized_functions = {}
#     for key, value in C_VAGUE_FUNCTIONS.items():
#         serialized_functions[key] = {
#             "code": base64.b64encode(value.__code__.co_code).decode("utf-8"),
#             "name": value.__name__,
#             "argcount": value.__code__.co_argcount,
#             "varnames": value.__code__.co_varnames,
#             "filename": value.__code__.co_filename,
#             "name": value.__code__.co_name,
#             "qualname": value.__code__.co_name,  # Python 3.3+
#             "firstlineno": value.__code__.co_firstlineno,
#             "lnotab": base64.b64encode(value.__code__.co_lnotab).decode("utf-8")
#        }

#     with open("vague_functions.json", "w") as f:
#         json.dump(serialized_functions, f)
    
# def deserialize_function(serialized_func):
#     code = base64.b64decode(serialized_func['code'])
#     lnotab = base64.b64decode(serialized_func['lnotab'])
#     code_obj = types.CodeType(
#         serialized_func['argcount'],
#         0,  # positionalonlyargcount (Python 3.8+)
#         0,  # kwonlyargcount (Python 3.0+)
#         len(serialized_func['varnames']),
#         64,  # stacksize (arbitrary value)
#         67,  # flags (arbitrary value)
#         code,
#         (),  # constants (arbitrary empty tuple)
#         (),  # names (arbitrary empty tuple)
#         tuple(serialized_func['varnames']),
#         serialized_func['filename'],
#         serialized_func['name'],
#         serialized_func['name'],  # Python 3.3+
#         serialized_func['firstlineno'],
#         lnotab,
#         b""
#     )
#     return types.FunctionType(code_obj, globals())

# def inject_function(serialized_func, use_frame):
#     deserialized_func = deserialize_function(serialized_func)
#     # parent_frame = use_frame.f_back
#     # parent_locals = parent_frame.f_locals
#     locals = use_frame.f_locals

#     # now we want to inject the function into the parent frame.
#     locals[serialized_func['name']] = deserialized_func

# def load_vague_functions():
#     print ("Loading vague functions...")
#     global C_VAGUE_FUNCTIONS

#     # load the cache of functions from a file.

#     try:
#         with open("vague_functions.json") as f:
#             serialized_functions = json.load(f)
#     except FileNotFoundError:
#         return {}
    
#     vague_functions = {}
#     # frame = inspect.currentframe().f_back.f_back
#     # caller_locals = frame.f_locals
#     parent_frame = inspect.currentframe().f_back
#     parent_locals = parent_frame.f_locals
#     for key, value in serialized_functions.items():
#         inject_function(value, parent_frame)

#         vague_functions[key] = parent_locals[value['name']]

#     C_VAGUE_FUNCTIONS = vague_functions

#     return vague_functions

C_FUNCTION_CODES = None

def save_function_codes():
    # print ("Saving function code...")
    # save the cache of functions to a file.
    with open("function_code.json", "w") as f:
        json.dump(C_FUNCTION_CODES, f, indent=2)

def load_function_codes():
    # print ("Loading function code...")
    global C_FUNCTION_CODES

    try:
        with open("function_code.json") as f:
            C_FUNCTION_CODES = json.load(f)
    except FileNotFoundError:
        C_FUNCTION_CODES = {}

    return C_FUNCTION_CODES

def inject_function_codes(local_frame):
    global C_VAGUE_FUNCTIONS
    if C_VAGUE_FUNCTIONS is None:
        C_VAGUE_FUNCTIONS = {}
    # print ("Injecting function code...")
    # inject the function code into the current module.
    locals = local_frame.f_locals
    for key, value in C_FUNCTION_CODES.items():
        function_code = value["function_code"]
        function_name = value["function_name"]
        compiled_function = compile(function_code, "<string>", "exec")
        exec(compiled_function, globals(), locals)
        C_VAGUE_FUNCTIONS[key] = locals[function_name]

def vague(instructions, client=None):
    '''
    A function that takes a set of instructions, and attempts to turn those instructions into a python function.
    It uses an LLM to generate the function based on the instructions, and includes access to locals and 
    globals in generating the function. It returns the result of the function. The general approach is:
    - If a function has already been generated for the instructions, call it and return the result.
    - Otherwise, generate a prompt including the instructions, and information about the locals and globals,
    and ask a code generating LLM to generate a function. Cache the function for later, call it, and return the result.
    '''
    MODEL="gpt-4o"
    client = client or get_client()

    global C_FUNCTION_CODES
    if C_FUNCTION_CODES is None:
        load_function_codes()
        inject_function_codes(inspect.currentframe().f_back)

    global C_VAGUE_FUNCTIONS
    # print (f"C_VAGUE_FUNCTIONS: {C_VAGUE_FUNCTIONS}")

    # get the locals and globals. We want to pass just the keys, not the values.
    frame = inspect.currentframe().f_back
    caller_locals = frame.f_locals
    locals_keys = list(caller_locals.keys())
    # locals_keys = list(locals().keys())
    globals_keys = list(globals().keys())

    # print (f"locals_keys: {locals_keys}")
    # print (f"globals_keys: {globals_keys}")

    instructions_hash = hash_instructions(instructions)

    if instructions_hash in C_VAGUE_FUNCTIONS:
        # print (f"Function already generated. caller_locals: {caller_locals}") 
        return C_VAGUE_FUNCTIONS[instructions_hash](caller_locals)

    prompt = f"""
Generate a python function based on the following instructions. It should take only one argument,
locals, and return a result. The locals argument will be a dictionary containing the locals 
of the calling function. Use the locals to access variables in the calling function. You can also 
look for names in the globals.

Note: If you need to use any import statements, include them inside the function definition.
--begin instructions--
{instructions}
--end instructions--

The instructions might be referring to the following locals: {locals_keys}
The instructions might be referring to the following globals: {globals_keys}

Return a JSON document, with the def statement as the attribute "function_code" and the name of the function as the attribute "function_name". 
"""

    tries_left = 3
    while tries_left > 0:
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system", "content": "You are an intelligent code assistant. Generate a function based on the instructions."},
                    {"role": "user", "content": prompt}
                ]
            )

            json_response = json.loads(completion.choices[0].message.content)
            # print (f"json_response: {json_response}")
            function_code = json_response.get("function_code")
            function_name = json_response.get("function_name")

            # if the function_code doesn't begin with "def", then we need to try again.
            if function_code is None or not function_code.startswith("def"):
                raise Exception("Function code not generated.")

            # compile the function
            compiled_function = compile(function_code, "<string>", "exec")

            # execute the def statement
            exec(compiled_function, globals(), locals())

            # extract the function from the locals
            generated_function = locals()[function_name]

            break
        except Exception as e:
            # print (f"Error: {e}")
            tries_left -= 1
            continue

    C_FUNCTION_CODES[instructions_hash] = {
        "function_code": function_code,
        "function_name": function_name
    }
    save_function_codes()


    # cache the function
    C_VAGUE_FUNCTIONS[instructions_hash] = generated_function

    # call the function
    return generated_function(caller_locals)
