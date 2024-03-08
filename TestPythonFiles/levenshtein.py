def levenshtein(s1, s2):
    # Initialize a matrix to store the Levenshtein distances
    matrix = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]

    # Initialize the first row and column of the matrix
    for i in range(len(s1) + 1):
        matrix[i][0] = i
    for j in range(len(s2) + 1):
        matrix[0][j] = j

    # Compute Levenshtein distance for each pair of substrings
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            matrix[i][j] = min(matrix[i - 1][j] + 1,      # Deletion
                               matrix[i][j - 1] + 1,      # Insertion
                               matrix[i - 1][j - 1] + cost)  # Substitution

    # Return the Levenshtein distance between the last elements of s1 and s2
    return matrix[len(s1)][len(s2)]

# Example usage:
s1 = ["apple", "banana", "orange"]
s2 = ["aple", "banan", "orang"]
distance = levenshtein(s1, s2)
print("Levenshtein distance:", distance)
