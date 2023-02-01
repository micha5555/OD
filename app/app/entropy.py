from sys import argv
import math

def count_data_entropy(data):
    data = bytes(data, encoding='utf-8')
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