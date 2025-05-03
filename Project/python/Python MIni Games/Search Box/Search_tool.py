#import module
from googlesearch import search

print("WELCOME !!! GOOGLE SEARCH TOOL WELCOMES YOU")

# taking Queary

query = input("WHAT DO YOU WANT TO SEARCH ON GOOGLE ??? : ")

for i in search(query, start=0, stop=10):
    print(i)
