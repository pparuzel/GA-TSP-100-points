#!/usr/bin/env python3

import copy
import math
import random

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.path import Path

import data


class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        return math.hypot(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f'City({self.x:.2f}, {self.y:.2f})'


class Route:
    """
    Constructs random route
    from a list of cities OR a route from given genes
    """

    def __init__(self, cities=None, genes=None):
        if genes:
            self.cities = genes
        elif cities:
            self.cities = cities[:]
            random.shuffle(self.cities)
        else:
            self.cities = []
        self.fitness = 0
        self.chance = 0

    def evaluate_fitness(self):
        self.fitness = 1000 / self.length()

    def copy(self):
        clone = copy.deepcopy(self)
        return clone

    def length(self):
        distances = (self.cities[i].distance(self.cities[i + 1]) for i in range(-1, len(self.cities) - 1))
        return sum(distances)

    def __repr__(self):
        return f'<Route ({self.fitness:.2f})>'

    def __str__(self):
        return '->'.join(repr(city) for city in self.cities)


def evaluate_chances(pop):
    summed_fitness = sum(k.fitness for k in pop)
    for k in pop:
        k.chance = k.fitness / summed_fitness


def wheel_selection(pop):
    i = -1
    rand = random.random()
    while rand > 0:
        i += 1
        rand -= pop[i].chance
    return pop[i]


def tournament_selection(pop):
    chosen = []
    for i in range(2):
        candidates = [random.choice(pop) for _ in range(2)]
        chosen.append(max(candidates, key=lambda k: k.fitness))
    return max(chosen, key=lambda k: k.fitness)


def crossover(c1, c2):
    end = random.randint(0, len(c1.cities))
    start = random.randint(0, end)
    section = c1.cities[start:end + 1]
    leftovers = [gene for gene in c2.cities if gene not in section]
    left, right = leftovers[:start], leftovers[start:]
    return Route(genes=left + section + right)


def mutation(pop, rate):
    for k in pop:
        if random.random() < rate:
            r1 = random.randint(0, len(k.cities) - 1)
            r2 = random.randint(0, len(k.cities) - 1)
            pick = random.random()
            if pick < 1 / 3:
                k.cities[r1], k.cities[r2] = k.cities[r2], k.cities[r1]
            elif pick < 2 / 3:
                if r1 > r2:
                    r1, r2 = r2, r1
                k.cities[r1:r2] = k.cities[r1:r2][::-1]
            else:
                k.cities.insert(r2, k.cities.pop(r1))


def draw(best_indiv, distances, fitnesses):
    vertices = [(city.x, city.y) for city in best_indiv.cities] + [(None, None)]
    codes = [Path.LINETO] * len(best_indiv.cities)
    codes[0] = Path.MOVETO
    codes += [Path.CLOSEPOLY]
    path = Path(vertices, codes)
    fig = plt.figure(figsize=(12, 5))
    ax1 = fig.add_subplot(2, 2, (1, 3))
    patch = patches.PathPatch(path, facecolor='none', lw=1)
    ax1.add_patch(patch)
    ax1.set_xlim(-1, 11)
    ax1.set_ylim(-1, 11)
    plt.title('Path')
    ax1.plot(locations[:, 0], locations[:, 1], 'o')
    ax2 = fig.add_subplot(222)
    plt.title('Lowest distance', loc='left')
    ax2.plot(distances)
    ax3 = fig.add_subplot(224)
    plt.title('Highest fitness', loc='left')
    ax3.plot(fitnesses)
    plt.subplots_adjust(hspace=0.5)
    plt.show()


locations = data.LOCATIONS
all_cities = [City(*loc) for loc in locations]

'''
    Parameters
'''
POPULATION_SIZE = 50
MUTATION_RATE = 0.35
N_ITERATIONS = 5000
# selection = wheel_selection
selection = tournament_selection


def main(show_plot=True):
    population = [Route(all_cities) for _ in range(POPULATION_SIZE)]
    for individual in population:
        individual.evaluate_fitness()
    evaluate_chances(population)  # necessary if using wheel roulette selection

    best_ever = population[0].copy()  # always copy the best tracked
    distance_history = []
    fitness_history = []

    for iteration in range(N_ITERATIONS):
        new_population = []

        for i in range(POPULATION_SIZE):
            individual_1 = selection(population)
            individual_2 = selection(population)
            child = crossover(individual_1, individual_2)
            new_population.append(child)

        mutation(new_population, MUTATION_RATE)

        population = new_population
        for individual in population:
            individual.evaluate_fitness()
        evaluate_chances(population)  # necessary for wheel roulette selection

        best = max(population, key=lambda k: k.fitness)
        distance_history.append(best.length())
        fitness_history.append(best.fitness)
        print(f'Current best: {best!r} --- {iteration * 100 / N_ITERATIONS}%')
        if best_ever.fitness < best.fitness:
            best_ever = best.copy()

    print('All-time best:', repr(best_ever))
    print('Route length:', best_ever.length())
    if show_plot:
        draw(best_ever, distance_history, fitness_history)


if __name__ == '__main__':
    random.seed(14)  # Seed finding a promising (if not best) path
    main(show_plot=True)
