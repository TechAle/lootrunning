# import pandas lib as pd
import pandas as pd

coordsChests = []
output = "x,y,z"

with open("waypoints.txt", 'r') as file:
    # The first 3 lines are useless
    for i in range(3):
        file.readline()
    # Read every waypoint
    while line := file.readline():
        array = line.rstrip().split(":")
        # Get x-y-z
        coordsChests.append((int(array[3]), int(array[4]), int(array[5])))

# read by default 1st sheet of an excel file
df = pd.read_excel('waypoints.xlsx')

addedChests = []

newChests = 0
totalChests = 0
for x, y, z in zip(df[df.keys()[4]].to_numpy(), df[df.keys()[5]].to_numpy(), df[df.keys()[6]].to_numpy()):
    x, y, z = int(x[1:]), int(y[1:]), int(z[1:])
    found = None
    for chest in coordsChests:
        if abs(chest[0] - x) + abs(chest[2] - z) <= 50:
            found = chest
            break
    if found is None:
        newChests+=1
        found = (x, y, z)
    totalChests += 1
    addedChests.append((x, y, z))
    output += f"\n{x},{y},{z}"

print(f"New chests: {newChests} total chests: {totalChests}")

text_file = open("chests.csv", "w")
n = text_file.write(output)
text_file.close()
