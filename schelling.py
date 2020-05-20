# Sindri Ingolfsson
# 11/03/2020

import argparse
import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


def get_neighbours(x, y, g):
    return g[x - 1 : x + 2, y - 1 : y + 2]


def get_neighbours_location(x, y):
    return [
        (i, j)
        for i in range(x - 1, x + 2)
        for j in range(y - 1, y + 2)
        if grid[i, j] != 0
    ]


def happy(x, y, g):
    return happy_val(x, y, g) >= PREJUDICE


def happy_val(x, y, g):
    me = g[x, y]
    surrounding = get_neighbours(x, y, g)
    assert surrounding.shape == (3, 3)
    goodNeighbours = 0
    for agent in surrounding.flatten():
        if me == agent:
            goodNeighbours += 1
        elif agent == 0:
            goodNeighbours += 0.5
    return goodNeighbours


def switcheroo(x, y, grid):
    mehappy = happy(x, y, grid)
    unhappies = []
    happies = []

    for i, j in get_neighbours_location(x, y):
        if i == x and j == y:
            continue
        elif not happy(i, j, grid) and not mehappy and grid[x, y] != grid[i, j]:
            unhappies.append((i, j))
        elif (
            happy(i, j, grid)
            and not mehappy
            and grid[x, y] != grid[i, j]
            and grid[i, j] != 0
        ):
            if 9 - happy_val(i, j, grid) >= happy_val(x, y, grid):
                happies.append((i, j))
    if len(unhappies) != 0:  # Try to swap with some other unhappy agent
        nx, ny = random.choice(unhappies)
    elif len(happies) != 0:  # Swap with a happy agent if it doesn't make me worse off
        nx, ny = random.choice(happies)
    else:
        return (-1, -1)
    grid[x, y], grid[nx, ny] = grid[nx, ny], grid[x, y]
    return nx, ny


def add_frame(arr, ims):
    temp = plt.imshow(
        arr[1:-1, 1:-1], animated=True, vmin=0.70, vmax=args.players + 0.1
    )
    ims.append([temp])


def parse_arguments():
    parser = argparse.ArgumentParser(description="Schellings Segregation Model")
    parser.add_argument(
        "mode",
        choices=["gif", "image", "live"],
        help="should the program save the simulation as a gif, save the final result as a png or show the simulation on screen?",
    )
    parser.add_argument(
        "-n",
        "--name",
        default="schelling" + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
        help="name for the created gif",
    )
    parser.add_argument(
        "-s", "--size", type=int, default=50, help="Size of the simulation. Default:50"
    )
    parser.add_argument(
        "-g",
        "--groups",
        type=int,
        default=2,
        choices=[2, 3, 4],
        help="number of different groups in the model. default:2",
    )
    parser.add_argument(
        "-d",
        "--prejudice",
        type=int,
        default=4,
        choices=[1, 2, 3, 4, 5, 6, 7],
        help="How many similar neighbours the agents want to be happy: default:4",
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=8,
        help="number of simulation iterations performed. default:8",
    )
    parser.add_argument(
        "-m",
        "--moves_per_frame",
        type=int,
        default=0,
        help="number of moves per saved image in the gif. default:size/10+1",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        type=bool,
        default=True,
        help="Display additional information during runtime. default:True",
    )
    args = parser.parse_args()

    if args.moves_per_frame == 0:
        args.moves_per_frame = args.size // 10 + 1
    if args.iterations <= 0:
        print("Iterations must be positive")
    if args.moves_per_frame <= 0:
        print("moves_per_frame must be positive")
    args.prejudice += 1  # adjustmets because prejudice checks count the agent itself
    return args


if __name__ == "__main__":
    args = parse_arguments()
    SIZE = args.size
    PREJUDICE = args.prejudice

    # Initialisation
    fig = plt.figure(figsize=[SIZE / 10, SIZE / 10])
    plt.axis("off")

    fig.subplots_adjust(bottom=0, top=1, left=0, right=1)

    imgrid = []
    start = np.random.randint(low=1, high=args.players + 1, size=(SIZE, SIZE))
    grid = np.zeros((SIZE + 2, SIZE + 2))
    grid[1:-1, 1:-1] = start
    switchCount = 0

    # Keeping track of active agents speeds up processing
    active = [(i, j) for i in range(1, SIZE) for j in range(1, SIZE)]
    random.shuffle(active)
    active = set(active)
    nextActive = set()

    for iteration in range(args.iterations):
        if args.verbose:
            print("Iteration", iteration)
        for x, y in active:
            # do switches
            if not happy(x, y, grid):
                nx, ny = switcheroo(x, y, grid)
                if (nx, ny) != (-1, -1):
                    nextActive.update(get_neighbours_location(x, y))
                    nextActive.update(get_neighbours_location(nx, ny))
                    if args.mode == "gif" and switchCount % args.moves_per_frame == 0:
                        add_frame(grid, imgrid)
                    switchCount += 1

        active = nextActive
        nextActive = set()
        if args.verbose:
            print("Number of active agents: ", len(active))
    if args.verbose:
        print(f"Total number of switches: {switchCount}")

    # Saving
    if args.mode == "image":
        plt.imshow(grid[1:-1, 1:-1], vmin=0.75, vmax=args.players + 0.1)
        plt.savefig(f"images/{args.name}.png", bbox_inches="tight")
    if args.mode == "gif":
        print(f"Number of frames in gif: {len(imgrid)}")
        ani = animation.ArtistAnimation(
            fig, imgrid, interval=100, blit=False, repeat_delay=5000
        )
        ani.save(f"gifs/{args.name}.gif", writer="pillow", fps=60)
    if args.mode == "live":
        plt.show()
