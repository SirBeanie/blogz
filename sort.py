def sort(alist):
    sorted = False
    while sorted == False:
        number = 0
        for a in range(len(alist)-1):
            if alist[a].id < alist[a+1].id:
                (alist[a],alist[a+1]) = (alist[a+1],alist[a])
                number += 1
        if number == 0:
            sorted = True
    return alist
