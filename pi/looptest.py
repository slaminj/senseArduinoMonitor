print("startup")
def innerLoop():
    try:
        i = 0
        while True:
            print("inner loop ", i)
            i+= 1
            if (i == 4):
                j = j/0
    except:
        print("caught exception")

while True:
    print("outer loop start")
    innerLoop()
    print("outer loop end")
