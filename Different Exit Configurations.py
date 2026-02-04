import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap
import math
import random
from collections import deque


# room parameters

width = 12*4
height = 24*4
people_count = 444

# exits
exit_scenarios = [
    [(23, 92)],
    [(1, 1), (47, 1)],
    [(23, 1), (23, 92)],
    [(1, 1), (23, 23), (47, 1)],
    [(1, 1), (23, 92), (47, 1)],
    [(1, 1), (23, 90), (47, 1), (23, 23)],
]
scenario_names = [
    "1) (23,92)",
    "2) (1,1)+(47,1)",
    "3) (23,1)+(23,92)",
    "4) (1,1)+(23,23)+(47,1)",
    "5) (1,1)+(23,92)+(47,1)",
    "6) (1,1)+(23,90)+(47,1)+(23,23)",
]
scenario_idx = 0
results = []  # (name, time_steps)


# barriers / slow_zones

barriers = []

for x in range(20, 29):
    barriers.append((x, 22))

for y in range(22, 73):
    barriers.append((20, y))

for y in range(22, 73):
    barriers.append((28, y))

slow_zones = []

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

slow_set = set(slow_zones)


# grid
grid = [[0 for _ in range(width)] for _ in range(height)]


def expand_exits(exit_centers):
    global grid
    new_exits = []
    for door in exit_centers:
        x0, y0 = door
        if x0 == 1:
            for i in range(6):
                x = x0 + i
                if 0 <= x < width and 0 <= y0 < height:
                    grid[y0][x] = 2
                    new_exits.append((x, y0))
        elif x0 == 47:
            for i in range(6):
                x = x0 - i
                if 0 <= x < width and 0 <= y0 < height:
                    grid[y0][x] = 2
                    new_exits.append((x, y0))
        else:
            for i in range(-2, 5):
                x = x0 + i
                if 0 <= x < width and 0 <= y0 < height:
                    grid[y0][x] = 2
                    new_exits.append((x, y0))
    return new_exits


# distance map
def compute_distance_map(exits):
    dist_map = [[float('inf')] * width for _ in range(height)]
    q = deque()

    for ex, ey in exits:
        dist_map[ey][ex] = 0.0
        q.append((ex, ey))

    while q:
        x, y = q.popleft()
        d = dist_map[y][x]

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
                            q.append((nx, ny))

    return dist_map


#  move_person

def move_person(px, py):
    best_dist = distance_map[py][px]
    candidates = []

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue

            nx = px + dx
            ny = py + dy

            if 0 <= nx < width and 0 <= ny < height:
                if grid[ny][nx] == 0 or grid[ny][nx] == 2 or grid[ny][nx] == 4:
                    d = distance_map[ny][nx]
                    if d < best_dist:
                        candidates = [(nx, ny)]
                        best_dist = d
                    elif d == best_dist:
                        candidates.append((nx, ny))

    if candidates:
        return random.choice(candidates)
    return px, py



def reset_scenario():
    global grid, exits, distance_map, people, time_step

    
    grid = [[0 for _ in range(width)] for _ in range(height)]
    for bx, by in barriers:
        if 0 <= bx < width and 0 <= by < height:
            grid[by][bx] = 3
    for sx, sy in slow_zones:
        if 0 <= sx < width and 0 <= sy < height:
            grid[sy][sx] = 4

    
    exit_centers = exit_scenarios[scenario_idx]
    exits = expand_exits(exit_centers)

    # calcu distance_map
    distance_map = compute_distance_map(exits)

    
    people = []
    placed = 0
    while placed < people_count:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        if grid[y][x] == 0 or grid[y][x] == 4:
            people.append([x, y, 0])
            grid[y][x] = 1
            placed += 1

    time_step = 0


# plotting

fig, ax = plt.subplots()

colours = ['white', 'blue', 'green', 'black', 'red']
cmap = ListedColormap(colours)
image = ax.imshow(grid, vmin=0, vmax=4, cmap=cmap)

ax.set_xticks(range(width))
ax.set_yticks(range(height))
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.grid(True)

time_step = 0
people = []
exits = []
distance_map = None


reset_scenario()

# update
def update(frame):
    global grid, people, time_step, scenario_idx, animation

 
    if len(people) == 0:
        results.append((scenario_names[scenario_idx], time_step))
        print(f"[DONE] {scenario_names[scenario_idx]}  time_steps={time_step}")

        scenario_idx += 1
        if scenario_idx >= len(exit_scenarios):
            animation.event_source.stop()
            ax.set_title("All 6 scenarios finished. See console for summary.")
            print("\n=== SUMMARY ===")
            for name, t in results:
                print(f"{name}: {t}")
            return image,

        reset_scenario()
        image.set_data(grid)
        ax.set_title(f"{scenario_names[scenario_idx]} | Time steps: {time_step} | People left: {len(people)}")
        return image,

    
    new_grid = [[0 for _ in range(width)] for _ in range(height)]

    for bx, by in barriers:
        if 0 <= bx < width and 0 <= by < height:
            new_grid[by][bx] = 3

    for sx, sy in slow_zones:
        if 0 <= sx < width and 0 <= sy < height:
            new_grid[sy][sx] = 4

    for ex in exits:
        new_grid[ex[1]][ex[0]] = 2

    new_people = []

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
            if (nx, ny) in slow_set:
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
    
    ax.set_title(f"Time steps: {time_step} | People left: {len(people)}")

    return image,

# execute
animation = FuncAnimation(fig, update, interval=50)
plt.show()
