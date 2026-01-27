import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math

#room
width = 50
height = 30
people_count = 150
exits = [(1, 28),(25,2), (48, 28)]

#empty grid
grid = []
for y in range(height):
    row = []
    for x in range(width):
        row.append(0)
    grid.append(row)

#add exits and ppl
for ex in exits:
    grid[ex[1]][ex[0]] = 2
people = []
x = 2
y = 2
for i in range(people_count):
    people.append([x, y])
    grid[y][x] = 1
    x += 2
    if x >= width - 1:
        x = 2
        y += 2

#distance to exit
def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

#moving one person
def move_person(px, py):
    # find nearest exit
    nearest = exits[0]
    best_dist = distance(px, py, nearest[0], nearest[1])

    for ex in exits:
        d = distance(px, py, ex[0], ex[1])
        if d < best_dist:
            nearest = ex
            best_dist = d

    #try all nearby squares
    best_x = px
    best_y = py

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            nx = px + dx
            ny = py + dy

            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny][nx] == 0 or grid[ny][nx] == 2:
                    d = distance(nx, ny, nearest[0], nearest[1])
                    if d < best_dist:
                        best_dist = d
                        best_x = nx
                        best_y = ny

    return best_x, best_y

#plotting
fig, ax = plt.subplots()
image = ax.imshow(grid, vmin=0, vmax=2)

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
    if len(people) == 0:
        animation.event_source.stop()
        ax.set_title("Evacuated in " + str(time_step) + " time steps")
        return image,

    new_grid = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(0)
        new_grid.append(row)

    for ex in exits:
        new_grid[ex[1]][ex[0]] = 2

    new_people = []

    for person in people:
        px, py = person
        nx, ny = move_person(px, py)

        if grid[ny][nx] == 2:
            continue

        if new_grid[ny][nx] == 0:
            new_grid[ny][nx] = 1
            new_people.append([nx, ny])
        else:
            new_grid[py][px] = 1
            new_people.append([px, py])

    grid = new_grid
    people = new_people
    time_step += 1

    image.set_data(grid)
    ax.set_title("Time steps: " + str(time_step))

    return image,


#execute
animation = FuncAnimation(fig, update, interval=500)
plt.show()
