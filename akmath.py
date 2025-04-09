def median(*args):
    if len(args) == 1:
        iter = args[0]
    else:
        iter = args
    
    iter = list(iter)
    iter = sorted(iter)
    n = len(iter)
    mid = n // 2
    if n % 2 == 0:
        return (iter[mid - 1] + iter[mid])/2
    else:
        return iter[mid]

def mapping(x1, x2, y1, y2):
    '''
    returns a linear floating-point function f(x) such that 
    f(x1) == y1 and f(x2) == y2
    '''
    
    m = (y2 - y1) / (x2 - x1)
    
    return lambda x: m*(x-x1) + y1

def plane(x1,y1,z1, x2,y2,z2, x3,y3,z3):
    '''
    returns a linear floating-point function f(x,y) such that 
    f(x1,y1) == z1 and f(x2,y2) == z2 and f(x3,y3) == z3
    '''

    # Compute normal vector components
    A = (y2 - y1) * (z3 - z1) - (y3 - y1) * (z2 - z1)
    B = (z2 - z1) * (x3 - x1) - (z3 - z1) * (x2 - x1)
    C = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)

    # Compute D
    D = A * x1 + B * y1 + C * z1

    if C == 0:
        raise ValueError("The given points do not define a unique plane (C=0 case).")

    # Return the function f(x, y)
    return lambda x, y: (D - A * x - B * y) / C


def matmul(A, B):
    '''
    returns the product of two matrices A and B,
    each of type list or tuple of ints or floats.
    Also handles matrix-vector multiplication where B is a vector (1D list/tuple).
    Type checking is not fully implemented. 
    '''
    if not isinstance(A, (list, tuple)):
        raise ValueError("A must be a list or tuple")
    if not isinstance(B, (list, tuple)):
        raise ValueError("B must be a list or tuple")
        
    # Handle vector case - convert B to column vector if it's a 1D list/tuple
    B_is_vector = not any(isinstance(x, (list, tuple)) for x in B)
    if B_is_vector:
        B = [[x] for x in B]
        
    result = [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
    
    # If B was a vector, convert result back to 1D
    if B_is_vector:
        return [row[0] for row in result]
    return result

def I(n):
    '''
    returns the n x n identity matrix
    '''
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]

def _test():
    A = ([1,3], (0, 0))
    x = (9, 11)
    print(matmul(A, x))

if __name__ == "__main__":
    _test()
