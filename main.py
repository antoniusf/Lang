stack = []

def alpha_shift(string):
    new_string = ""
    for char in string:
        if char not in ["/", "-"]:
            new_string += chr(ord(char)+5)
        else:
            new_string += char
    return new_string

variable = "a"
def improve_alpha(string):
    global variable
    if string[0] == "/":
        head = string[:2]
        body = string[2:]
        own_variable = variable
        variable = chr(ord(variable)+1)
        body, string = improve_alpha(body)
        #print head[1], body, own_variable
        body = body.replace(head[1], own_variable)
        head = "/"+own_variable
        #print head, body
        return head+body, string
    elif string[0] == "-":
        head = string[0]
        operator = string[1:]
        operator, string = improve_alpha(operator)
        operand = string
        operand, string = improve_alpha(operand)
        return head+operator+operand, string
    else:
        return string[0], string[1:]

def lambdaeval(string, replace=None):
    if string == "":
        return string
    if string[0] == "/":
        head = string[:2]
        body = string[2:]
        body_processed, string = lambdaeval(body, replace=replace)
        #print "Abstraction: "+head+", "+body_processed
        return head+body_processed, string
    elif string[0] == "-":
        returnstring = string[0]
        operator, string = lambdaeval(string[1:], replace=replace)
        operand, string = lambdaeval(string, replace=replace)
        #print "Application: "+operator+", "+operand
        if replace == None:#Don't replace when there is already a replacement in progress
            if operator[0] == "/":#Check whether the operator is an abstraction and can thus be applied
                replacechar = operator[1]
                replacestring = operand
                result, a = lambdaeval(operator, replace=(replacechar, replacestring))
                result = result[2:]#Cap off the abstraction variable
                simplified_result, a = lambdaeval(result)#Check for newly created applications (and execute them)
                return simplified_result, string
        return returnstring+operator+operand, string
    else:
        if replace != None:
            if string[0] == replace[0]:
                return replace[1], string[1:]
            else:
                return string[0], string[1:]
        else:
            return string[0], string[1:]

def input_eval(string):
    global variable
    result = lambdaeval(improve_alpha(string.upper())[0])[0]
    variable = "a"
    result = improve_alpha(result.upper())
    variable = "a"
    return result[0]

a = "/f/xx"
b = "/f/x-"

symbols = { "a": "/a/bb", "b": "/a/ba", "c": "/a--a/b/cc/d/ed", "d": "/a/b/c-b--abc", "e": "/a/b-ab", "f": "/a/b-a-ab", "g": "/a/b/c--cab" }
reverse_symbols = {v:k for k, v in symbols.items()}

if __name__ == "__main__":

    while True:
        exp = raw_input("")
        if exp == "q":
            break
        length = len(exp)
        new_exp = "-"*(length-1)
        for char in exp:
            new_exp += symbols[char]
        result = input_eval(new_exp)
        if result in reverse_symbols.keys():
            print reverse_symbols[result]
        print result
