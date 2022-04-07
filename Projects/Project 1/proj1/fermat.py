import random


def prime_test(N, k):
    # This is main function, that is connected to the Test button. You don't need to touch it.
    return fermat(N, k), miller_rabin(N, k)


# Calculate x^y mod N
# Time complexity: O(n^3) for n being the chars in x and y.
#   n recursive calls with n^2 complexity per call
# Space complexity: O(n) as each recursive call creates new ints on the stack
def mod_exp(x, y, N):
    if y == 0:
        return 1  # Base case
    z = mod_exp(x, y // 2, N)  # Recursive Call with floor(y/2), n calls
    if y % 2 == 0:  # if y is even return z^2
        return (z * z) % N
    else:  # if y is uneven return z^2 * x
        return (x * z * z) % N  # modular multiplication is n^2 for chars


# returns 1 minus the chance that the fermat tests were all false positives which is 1/2
def fprobability(k):
    return 1 - 2 ** -k


# same as fermat probability above except that each test has only a 1/4 probability of being wrong
def mprobability(k):
    return 1 - 4 ** -k


# Fermat's primality tester for number N with k tests
# Time complexity: O(n^3) as each mod_exp call is 0(n^3) for length on N
# Space complexity: O(n) as each call to mod_exp will be O(n) for space with k calls
def fermat(N, k):
    for i in range(k):  # k loops will do k tests of N
        a = random.randint(4, N - 2)  # choose random int in range 4 - (N-2) to avoid corner cases
        if mod_exp(a, N - 1, N) != 1:  # calc. a^(N-1) mod N which should be 1 if N is prime
            return "composite"
    return 'prime'  # if N does not fail any of the tests, return prime


# Miller Rabin primality test for number N with k tests
# Time complexity: O(n^4) for n calls to mod_exp with n^3 complexity
# Space complexity: O(n) as while loop writes over variables but mod_exp uses n space
def miller_rabin(N, k):
    for i in range(k):  # will loop k times perform k tests
        a = random.randint(4, N - 2)  # choose random int in range 4 - (N-2) to avoid corner cases
        e = N - 1  # sets the exponent to N-1 which will be modified in the while loop
        if mod_exp(a, e, N) != 1:  # if the first test is not 1 then N is composite
            return 'composite'
        while e % 2 == 0:  # Loop while exponent can be halved (n calls)
            e = e // 2  # Halve exponent
            if mod_exp(a, e, N) != 1:  # Once mod_exp does not equal 1 (O(n^3) complexity)
                if mod_exp(a, e, N) != N - 1:  # if next mod_exp does not equal -1
                    return 'composite'  # Than N is not prime
                break
    return 'prime'  # If N passes k tests, return prime
