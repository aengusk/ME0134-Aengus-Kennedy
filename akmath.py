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

def matsum(A, B):
    '''
    returns the sum of two matrices A and B,
    each of type list or tuple of ints or floats.
    '''
    return [list(map(sum, zip(*rows))) for rows in zip(A, B)]

def mat_inverse(A):
    # Make sure A is square
    n = len(A)
    for row in A:
        if len(row) != n:
            raise ValueError("Matrix must be square")

    # Create augmented matrix [A | I]
    AM = [list(row) + [float(i == j) for j in range(n)] for i, row in enumerate(A)]

    # Perform Gauss-Jordan elimination
    for i in range(n):
        # Find pivot
        pivot = AM[i][i]
        if pivot == 0:
            # Try to swap with a lower row
            for j in range(i + 1, n):
                if AM[j][i] != 0:
                    AM[i], AM[j] = AM[j], AM[i]
                    pivot = AM[i][i]
                    break
            else:
                raise ValueError("Matrix is singular and cannot be inverted")

        # Normalize pivot row
        for j in range(2 * n):
            AM[i][j] /= pivot

        # Eliminate other rows
        for k in range(n):
            if k != i:
                factor = AM[k][i]
                for j in range(2 * n):
                    AM[k][j] -= factor * AM[i][j]

    # Extract inverse matrix from augmented matrix
    inverse = [row[n:] for row in AM]
    return inverse

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
