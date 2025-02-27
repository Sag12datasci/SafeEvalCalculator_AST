import ast
import operator as op


# Supported operators
allowed_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Pow: op.pow,
    ast.USub: op.neg,   # Unary subtraction
    ast.Mod: op.mod,    # Modulus
    ast.Eq: op.eq,      # Equal
    ast.NotEq: op.ne,   # Not equal
    ast.Lt: op.lt,      # Less than
    ast.LtE: op.le,     # Less than or equal
    ast.Gt: op.gt,      # Greater than
    ast.GtE: op.ge,     # Greater than or equal
}


# Define a limit for the exponent
EXPONENT_LIMIT = 100

def _evaluate_node(node):
    try:
        if isinstance(node, ast.Constant):#In the context of the Abstract Syntax Tree (AST), a node is essentially a piece of the code'
            if isinstance(node.value, (int, float, complex)):#node.value simply means the actual value stored within a specific node.
                return (True, node.value)
            elif hasattr(node, 'n') and isinstance(node.n, (int, float, complex)): #In earlier versions of the AST, numeric constants were represented using the n attribute instead of the value attribute. So, this line of code is essentially a fallback mechanism to handle such cases.
                return (True, node.n)
            else:
                return (False, "Please enter only numbers or complex numbers in this expression")

        elif isinstance(node, ast.BinOp):
            success_left, left = _evaluate_node(node.left)
            #success_left will be True or False, indicating whether the evaluation was successful.
            #left will hold the actual evaluated value (the result of the evaluation).
            if not success_left:
                return (False, left)
            success_right, right = _evaluate_node(node.right)
            if not success_right:
                return (False, right)
            if type(node.op) in allowed_operators:#For example, in the expression 3 + 5, node.op would represent the + operator.
                if type(node.op) == ast.Pow and abs(right) > EXPONENT_LIMIT:#This checks if the absolute value of the right operand (the exponent) is greater than a predefined limit
                    return (False, f"Exponent {right} exceeds the limit of {EXPONENT_LIMIT}")

                try:
                    return (True, allowed_operators[type(node.op)](left, right))
                except ZeroDivisionError:
                    return (False, "Division by zero is not allowed")#not for pow , for div
            else:
                return (False, "Unsupported operator. Please use a valid operator.")


        elif isinstance(node, ast.UnaryOp) and type(node.op) in allowed_operators:#A unary operation involves only one operand, like negation (-x).
            success_operand, operand = _evaluate_node(node.operand)#-x where x is the operand  
            if not success_operand:
                return (False, operand)
            return (True, allowed_operators[type(node.op)](operand))#Unary Operations: Involve one operand

        elif isinstance(node, ast.Compare):
            success_left, left = _evaluate_node(node.left)#The evaluated value of the left operand (left) is necessary for performing the actual comparison or operation.
            if not success_left:
                return (False, left)
            result = []
            for comparator, operator in zip(node.comparators, node.ops):
                success_right, right = _evaluate_node(comparator)
                if not success_right:
                    return (False, right)
                
                if type(operator) in allowed_operators:
                    result.append(allowed_operators[type(operator)](left, right))
                    left = right
                    """This updates the left variable to the value of right for the next comparison in a chain.
                        This is necessary for handling chained comparisons, like 3 < 5 < 7. After evaluating 3 < 5, it uses 5 for the next comparison 5 < 7."""
                else:
                    return (False, "Unsupported comparison operator. Please use a valid operator.")
            return (True, all(result))

        else:
            return (False, "Unsupported expression type. Please provide a valid input type.")
    except Exception as e:
        return (False, str(e))

def evaluate_expression(expr):
    try:
        tree = ast.parse(expr, mode='eval')
        if not isinstance(tree, ast.Expression):
            return (False, "Invalid expression")
        return _evaluate_node(tree.body)

    except (ValueError, TypeError, SyntaxError) as e:
        if hasattr(e, 'lineno') and hasattr(e, 'offset'):
            return (False, f"Error: {e} at line {e.lineno}, column {e.offset}")
        return (False, f"Error: {e}")
    except Exception as e:
        return (False, "An error occurred: Malformed or unsafe expression.")

def is_exponent_exceed_limit(expression):
    try:
        tree = ast.parse(expression, mode='eval')
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                right = _evaluate_node(node.right)[1]
                if abs(right) > EXPONENT_LIMIT:
                    return True
        return False
    except Exception as e:
        return True

def factorial(x):
    if x == 0 or x == 1:
        return 1
    return x * factorial(x - 1)

def fibonacci(x):
    if x <0 :
        return (-1)**(x-1) * fibonacci(-x)
    elif x == 0:
        return 0
    elif x == 1:
        return 1
    else:
        return fibonacci(x - 1) + fibonacci(x - 2)

def table(x):
    if x == 0:
        return 'Multiplicative property of zero'
    results = [f'{x} X {i} = {x * i}' for i in range(1, 11)]
    return "\n".join(results)

# User-friendly interface
def main():
    print("Welcome to the Enhanced Calculator!")
    print("Type 'exit' or Press Ctril + C to end the program.")
    
    while True:
        try:
            expression = input("\nEnter a mathematical expression or a special function (factorial, fibonacci, table): ").strip().lower()
            if expression == "exit":
                print("Thank you for using the calculator. Goodbye!")
                break

            if expression == "factorial" or expression == "fibonacci" or expression == 'table':
                num = int(input(f"Enter a number to calculate its {expression}: "))
                if expression =="factorial":
                    print(f"Factorial of {num} : {factorial(num)}")
                elif expression =='fibonacci':
                    print(f"Fibonaci of {num} : {fibonacci(num)}")
                elif expression == "table":
                    num = int(input("Enter a number for the table: "))
                    print(f"Multiplication table for {num}:\n{table(num)}")
                continue

            if is_exponent_exceed_limit(expression):
                print(f"Exponent exceeds the limit of {EXPONENT_LIMIT}. Please enter a valid expression.")
            else:
                success, result = evaluate_expression(expression)
                if success:
                    print(f"Result: {result}")
                else:
                    print(f"Error: {result}")

        except KeyboardInterrupt:
            print("\nExiting the program...")
            break
        except ValueError:
            print("Invalid input. Please enter a valid number or expression.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

