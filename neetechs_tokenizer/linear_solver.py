# neetechs_tokenizer/linear_solver.py

import numpy as np

def gaussian_elimination(A: list, b: list) -> list:
    """
    Solve Ax = b using Gaussian elimination with back-substitution.
    A: Coefficient matrix
    b: Right-hand side vector
    Returns list of solutions x
    """
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float).reshape(-1, 1)
    n = len(b)

    # Forward elimination
    for i in range(n):
        # Pivoting
        max_row = np.argmax(abs(A[i:, i])) + i
        A[[i, max_row]] = A[[max_row, i]]
        b[[i, max_row]] = b[[max_row, i]]

        for j in range(i + 1, n):
            factor = A[j][i] / A[i][i]
            A[j] = A[j] - factor * A[i]
            b[j] = b[j] - factor * b[i]

    # Back substitution
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - np.dot(A[i][i + 1:], x[i + 1:])) / A[i][i]

    return x.tolist()

# Example usage
if __name__ == "__main__":
    A = [[2, 3], [1, -1]]
    b = [5, 1]
    sol = gaussian_elimination(A, b)
    print("Solution:", sol)
