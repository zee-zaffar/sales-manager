def binary_gap(N):
    binary = bin(N)[2:]
    gaps = binary.strip('0').split('1')
    return max((len(gap) for gap in gaps), default=0)

# Test
print(binary_gap(529))  # Output: 4

#Rotate an array K times to the right
def array_rotation(A,K):
    if not A:
        return A
    k = K % len(A)
    return A[-K:] + A[:-K]

# Test
print(array_rotation([3, 8, 9, 7, 6], 3))  # Output: [9, 7, 6, 3, 8]

#Find the element in an array that occurs an odd number of times.
def odd_occurrences(arr):
    result = 0
    for number in arr:
        result ^= number  # XOR cancels out even occurrences
    return result

# Test
print(odd_occurrences([9, 3, 9, 3, 9, 7, 9]))  # Output: 7

#A frog needs to jump from position start to at least end with jumps of length length. Find the minimum number of jumps.
def frog_jump(start, end, length):
    return -(- (end - start) // length)  # Equivalent to ceil((end - start) / length)
    
# Test
print(frog_jump(10, 85, 30))  # Output: 3

# Find the missing element in a permutation of numbers from 1 to N+1.
# Permutation is true, when numbers appears from 1 to n+1 without missing any numbers
def perm_missing_element(A):
    n = len(A) + 1
    total = n * (n + 1) // 2 
    return  total - sum(A)

# Test
print(perm_missing_element([2, 3, 1, 5]))  # Output: 4

#Count numbers divisible by divBy between num1 and num2.
def count_div(num1, num2, divBy):
    return num2 // divBy - (num1 - 1) // divBy

# Test
print(count_div(6, 11, 2))  # Output: 3 (6, 8, 10)


