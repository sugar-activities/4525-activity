#load_save.py
import g

loaded=[] # list of strings

def load(f):
    global loaded
    try:
        for line in f.readlines():
            loaded.append(line)
    except:
        pass

def save(f):
    f.write(str(g.level)+'\n')
    for n in g.scores: f.write(str(n)+'\n')

# note need for rstrip() on strings
def retrieve():
    global loaded
    if len(loaded)>0:
        g.level=int(loaded[0])
        for ind in range(4): g.scores[ind]=int(loaded[ind+1])
            


    
