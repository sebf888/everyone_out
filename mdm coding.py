import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
import math
import random

#room

# estimated priory road lecture theatre to be about 12*24 but not sure
# multiplied metres by 4 to make each person 0.25x0.25m**2
width = 12*4
height = 24*4
# capacity of priory road
people_count = 444
# again, guessed these but look pretty right
exits = [(1, 1), (23,23), (47, 1)]

barriers = []

#top barrier (behind downstairs exit)
for x in range(20, 29):  
    barriers.append((x, 22))

#left barrier
for y in range(22, 73):  
    barriers.append((20, y))

#right barrier
for y in range(22, 73):
    barriers.append((28, y))

# in slow zones people take 2 time steps to make a move
# currently only have slow zones between rows (could also add them on stairs?)
slow_zones = []


# generating uncrossable rows of seats
for y in range(23, 73, 3):
    for x in range(3, 20):
        barriers.append((x, y))

    if y + 1 < 73:
        for x in range(3, 20):
            slow_zones.append((x, y + 1))
    if y + 2 < 73:
        for x in range(3, 20):
            slow_zones.append((x, y + 2))


for y in range(23, 73, 3):
    for x in range(29, width - 3):  
        barriers.append((x, y))
    if y + 1 < 73:
        for x in range(29, width - 3):
            slow_zones.append((x, y + 1))
    if y + 2 < 73:
        for x in range(29, width - 3):
            slow_zones.append((x, y + 2))

for y in range(height - 20, height - 10, 3):  
    for x in range(5, width - 5): 
        barriers.append((x, y))
    if y + 1 < height:
        for x in range(5, width - 5):
            slow_zones.append((x, y + 1))
    if y + 2 < height:
        for x in range(5, width - 5):
            slow_zones.append((x, y + 2))
        

        




#empty grid
grid = []
for y in range(height):
    row = []
    for x in range(width):
        row.append(0)
    grid.append(row)
# print(grid)

# add barriers to grid
for barrier in barriers:
    bx, by = barrier
    if 0 <= bx < width and 0 <= by < height:
        grid[by][bx] = 3
    
# add slow zones to grid    
for slow in slow_zones:
    sx, sy = slow
    if 0 <= sx < width and 0 <= sy < height:
        grid[sy][sx] = 4
# for door in exits:
        
        
#add exits and ppl
new_exits = [] 
for door in exits:
    if door[0] == 1: 
        for i in range(6):
            grid[door[1]][door[0] + i] = 2
            new_exits.append((door[0] + i, door[1]))
    elif door[0] == 47:  
        for i in range(6):
            grid[door[1]][door[0] - i] = 2
            new_exits.append((door[0] - i, door[1]))
    else:  
        for i in range(-2, 5):
            grid[door[1]][door[0] + i] = 2
            new_exits.append((door[0] + i, door[1]))

exits = new_exits
    

# print(grid)

people = []
# x = 2
# y = 2
# for i in range(people_count):
#     people.append([x, y])
#     grid[y][x] = 1
#     x += 2
#     if x >= width - 1:
#         x = 2
#         y += 2

# randomly plot people
# could change them to all start in seats + a lecturer
people = []
placed = 0
while placed < people_count:
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    if grid[y][x] == 0 or grid[y][x] == 4:
        people.append([x, y, 0])
        grid[y][x] = 1
        placed += 1

# print(grid)


# euclidian distance to exit
def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

#moving one person
# def move_person(px, py):
#     # find nearest exit
#     nearest = exits[0]
#     best_dist = distance(px, py, nearest[0], nearest[1])

#     for ex in exits:
#         d = distance(px, py, ex[0], ex[1])
#         if d < best_dist:
#             nearest = ex
#             best_dist = d

#     #try all nearby squares
#     best_x = px
#     best_y = py

#     for dx in [-1, 0, 1]:
#         for dy in [-1, 0, 1]:
#             nx = px + dx
#             ny = py + dy

#             if 0 <= nx < width and 0 <= ny < height:
#                 if grid[ny][nx] == 0 or grid[ny][nx] == 2:
#                     d = distance(nx, ny, nearest[0], nearest[1])
#                     if d < best_dist:
#                         best_dist = d
#                         best_x = nx
#                         best_y = ny

#     return best_x, best_y

# def move_person(px, py):
#     # Find nearest exit
#     nearest = exits[0]
#     best_dist = distance(px, py, nearest[0], nearest[1])
#     for ex in exits:
#         d = distance(px, py, ex[0], ex[1])
#         if d < best_dist:
#             nearest = ex
#             best_dist = d
    
#     # Try all nearby squares
#     best_x = px
#     best_y = py
#     for dx in [-1, 0, 1]:
#         for dy in [-1, 0, 1]:
#             nx = px + dx
#             ny = py + dy
#             if 0 <= nx < width and 0 <= ny < height:
#                 # Allow movement to empty cells (0) or exits (2), but NOT barriers (3)
#                 if grid[ny][nx] == 0 or grid[ny][nx] == 2 or grid[ny][nx] == 4:
#                     d = distance(nx, ny, nearest[0], nearest[1])
#                     if d < best_dist:
#                         best_dist = d
#                         best_x = nx
#                         best_y = ny
#     return best_x, best_y

# Run this once at startup, before animation
def compute_distance_map():
    dist_map = [[float('inf')] * width for _ in range(height)]
    queue = []
    
    # Start from all exits
    for ex, ey in exits:
        dist_map[ey][ex] = 0
        queue.append((ex, ey, 0))
    
    # Flood fill
    while queue:
        x, y, d = queue.pop(0)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if grid[ny][nx] != 3:  # Not a barrier
                        new_dist = d + math.sqrt(dx*dx + dy*dy)
                        if new_dist < dist_map[ny][nx]:
                            dist_map[ny][nx] = new_dist
                            queue.append((nx, ny, new_dist))
    
    return dist_map

# Call before animation starts
distance_map = compute_distance_map()

# Then modify move_person to use it:
def move_person(px, py):
    best_x = px
    best_y = py
    best_dist = distance_map[py][px]
    
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx = px + dx
            ny = py + dy
            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny][nx] == 0 or grid[ny][nx] == 2 or grid[ny][nx] == 4:
                    if distance_map[ny][nx] < best_dist:
                        best_dist = distance_map[ny][nx]
                        best_x = nx
                        best_y = ny
    
    return best_x, best_y


#plotting
fig, ax = plt.subplots()

colours = ['white',    # 0 = empty space
          'blue',     # 1 = people
          'green',    # 2 = exits
          'black',    # 3 = barriers
          'red']   # 4 = slow zones

cmap = ListedColormap(colours)
image = ax.imshow(grid, vmin=0, vmax=4, cmap=cmap)

# image = ax.imshow(grid, vmin=0, vmax=4)

ax.set_xticks(range(width))
ax.set_yticks(range(height))
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.grid(True)

time_step = 0

#animating the movements
def update(frame):
    global grid, people, time_step, animation

    #stop when room is empty
    # if len(people) == 0:
    #     animation.event_source.stop()
    #     ax.set_title("Evacuated in " + str(time_step) + " time steps")
    #     return image,
    
    if len(people) == 0:
        time_step = 0
        people = []
        placed = 0
        while placed < people_count:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if grid[y][x] == 0 or grid[y][x] == 4:
                people.append([x, y, 0])
                placed += 1
        return image,

    new_grid = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(0)
        new_grid.append(row)

    for barrier in barriers:
        bx, by = barrier
        if 0 <= bx < width and 0 <= by < height:
            new_grid[by][bx] = 3
    
    for slow in slow_zones:
        sx, sy = slow
        if 0 <= sx < width and 0 <= sy < height:
            new_grid[sy][sx] = 4        
        

    for ex in exits:
        new_grid[ex[1]][ex[0]] = 2

    new_people = []

    # for person in people:
    #     px, py = person
    #     nx, ny = move_person(px, py)

    #     if grid[ny][nx] == 2:
    #         continue

    #     if new_grid[ny][nx] == 0:
    #         new_grid[ny][nx] = 1
    #         new_people.append([nx, ny])
    #     else:
    #         new_grid[py][px] = 1
    #         new_people.append([px, py])
    
    for person in people:
        px, py, wait_time = person
        
        if wait_time > 0:
            new_grid[py][px] = 1
            new_people.append([px, py, wait_time - 1])
            continue
        
        nx, ny = move_person(px, py)

        if grid[ny][nx] == 2:
            continue

        if new_grid[ny][nx] == 0 or new_grid[ny][nx] == 4:
            new_grid[ny][nx] = 1
            if (nx, ny) in [(s[0], s[1]) for s in slow_zones]:
                new_people.append([nx, ny, 1])
            else:
                new_people.append([nx, ny, 0])
        else:
            new_grid[py][px] = 1
            new_people.append([px, py, 0])

    grid = new_grid
    people = new_people
    time_step += 1

    image.set_data(grid)
    ax.set_title("Time steps: " + str(time_step))

    return image,


#execute
animation = FuncAnimation(fig, update, interval=50)
plt.show()
