import sqlite3

conn = sqlite3.connect('spider.sqlite')
cur = conn.cursor()

print("Creating JSON output on spider.js...")
howmany = int(input("How many nodes? "))

#basically joining the links...and ordering by no. of inbound links...
cur.execute('''SELECT COUNT(from_id) AS inbound, old_rank, new_rank, id, url 
    FROM Pages JOIN Links ON Pages.id = Links.to_id
    WHERE html IS NOT NULL AND ERROR IS NULL
    GROUP BY id ORDER BY id,inbound''')




#then the stuff we have selected above...we will be reading thru it
#we are looking for highest & lowest pagerank...
fhand = open('spider.js','w')
nodes = list()
maxrank = None
minrank = None
for row in cur :
    nodes.append(row)
    rank = row[2]
    if maxrank is None or maxrank < rank: maxrank = rank
    if minrank is None or minrank > rank : minrank = rank
    if len(nodes) > howmany : break

if maxrank == minrank or maxrank is None or minrank is None:
    print("Error - please run sprank.py to compute page rank")
    quit()

fhand.write('spiderJson = {"nodes":[\n')
count = 0
map = dict()
ranks = dict()
for row in nodes :
    if count > 0 : fhand.write(',\n')
    # print row
    rank = row[2]

    #we have written the Javascript below....viz lines and all..
    #we are basically normalising the rank
    rank = 19 * ( (rank - minrank) / (maxrank - minrank) ) 
    fhand.write('{'+'"weight":'+str(row[0])+',"rank":'+str(rank)+',')
    fhand.write(' "id":'+str(row[3])+', "url":"'+row[4]+'"}')
    #weight is how big the circle is
    '''in spider.js basically the source, target & value it tells of where the line starts where it ends 
    how big the line is and ....'''


    map[row[3]] = count
    ranks[row[3]] = rank
    count = count + 1
fhand.write('],\n')

cur.execute('''SELECT DISTINCT from_id, to_id FROM Links''')
fhand.write('"links":[\n')

count = 0
for row in cur :
    # print row
    if row[0] not in map or row[1] not in map : continue
    if count > 0 : fhand.write(',\n')
    rank = ranks[row[0]]
    srank = 19 * ( (rank - minrank) / (maxrank - minrank) ) 
    fhand.write('{"source":'+str(map[row[0]])+',"target":'+str(map[row[1]])+',"value":3}')
    count = count + 1
fhand.write(']};')
fhand.close()
cur.close()

print("Open force.html in a browser to view the visualization")
