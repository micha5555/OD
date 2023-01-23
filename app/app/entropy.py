from sys import argv
import math

def count_file_entropy(file_name):
    f = open(file_name, "rb")
    data = f.read()

    N = len(data)
    n = {}
    for character in data:
        if character in n:
            n[character] = n[character] + 1
        else:
            n[character] = 1

    entropy = 0
    for x in range(256):
        if(x in n):
            entropy = entropy + (n[x]/N * math.log2(n[x]/N))
    entropy = -entropy
    return entropy