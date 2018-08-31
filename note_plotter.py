file = open("notes.txt", "r") 
notes = file.readlines()



for line in notes:
    if len(line.rstrip().split()) > 1:
