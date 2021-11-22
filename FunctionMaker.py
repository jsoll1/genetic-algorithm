import sys
import math
import random

Operators = ['+', '*', '/', '-']        #The set of operators that will be used in the constructed equations

Leaves = ['1', '0', '2', 'x']           #The set of variables/constants that will be used in the constructed equations

operatorChance = .5                     #In the typical trees, the odds that a given node will be an operator after the depth limit has been reached once

depthLimit = 4                          #Initial depth of the constructed trees

popSize = 500                           #Size of the population
minVal = -1
maxVal = 1
pointComparisons = 100                  #Number of points that we will compare the approximations to the test

tornSize = round(popSize/5)             #Number of members of a population that will compete in a tournament for selection for the next generation. The online resources I found suggested making this 20% of the population size,
                                        #so that's what I did

pointRate = .01                         #If a tree is chosen to be mutated, this is the odds that any individual node will have it's bit flipped

numGens = 50                            #Number of generations that we will run

terminalFitness = .1                    #The point where we judge that it is close enough to the equation to work

##Sets the points that we will be judging fitness on. This is done here so that there won't be generational differences in the fitness algorithm
testPoints = [None] * pointComparisons
for i in range(0, pointComparisons):
    testPoints[i] = random.uniform(minVal, maxVal)
bottomReached = 0

#The equation that the algorithm tries to approximate
def eq(x):
    return (x+4)*9

class Node:
    global Operators
    global Leaves
    global operatorChance
    global depthLimit

    #Creates a new node with initial parameters
    def __init__(self, nodeType, depth):
        self.left = None
        self.right = None
        if (nodeType <= operatorChance):
            self.val = random.choice(Operators)
            self.type = 0
        else:
            self.val = random.choice(Leaves)
            self.type = 1
        self.depth = depth
        self.fitness = None
        self.leavesBelow = self.type
        self.opsBelow = 1-self.type
        self.parent = None

    #Prints the subtree that the node is the head of
    def display(self):
        if(self.left != None):
            print("(", end = "")
            self.left.display()
        print("", self.val, end = "")
        if(self.right != None):
            self.right.display()
            print(")", end = "")


#Creates a new node, which can be an operator or leaf, unless the bottom has been reached by any node in which case it can only be a leaf            
def make_node(nodeDepth):
    global bottomReached
    nodeType = random.random()
    if nodeDepth == depthLimit or bottomReached == 1:
        bottomReached = 1
        nodeType = 1
    node = Node(nodeType, nodeDepth)
    return node


#Constructs a grow type tree, which randomly creates a tree until the depth limit has been reached, at which point it only constructs leaves
def tree_helper(current):
    leftLeaves = 0
    rightLeaves = 0
    leftOps = 0
    rightOps = 0
    if current.depth == depthLimit:
        return current
    if current.left == None and current.type == 0:
        current.left = make_node(current.depth + 1)
        tree_helper(current.left)
        leftLeaves = current.left.leavesBelow
        leftOps = current.left.opsBelow
        current.left.parent = current
    if current.right == None and current.type == 0:
        current.right = make_node(current.depth + 1)
        tree_helper(current.right)
        rightLeaves = current.right.leavesBelow
        rightOps = current.right.opsBelow
        current.right.parent = current
    current.leavesBelow += leftLeaves + rightLeaves
    current.opsBelow += leftOps + rightOps
    return current
    
#Creates a grow type tree
def make_tree():
    global bottomReached
    bottomReached = 0
    head = Node(0, 0)
    head = tree_helper(head)
    return head


#Creates a node that's a leaf it it's at the depth limit, and an operator if it hasn't been reached
def make_full_node(nodeDepth):
    if nodeDepth == depthLimit:
        node = Node(1, nodeDepth)
    else:
        node = Node(0, nodeDepth)
    return node

#A helper function that seeds a full type tree
def full_tree_helper(current):
    if(current.depth == depthLimit):
        return current
    if current.left == None:
        current.left = make_full_node(current.depth+1)
        full_tree_helper(current.left)
    if(current.right == None):
        current.right = make_full_node(current.depth+1)
        full_tree_helper(current.right)
    current.leavesBelow += current.left.leavesBelow + current.right.leavesBelow
    current.opsBelow += current.left.opsBelow + current.right.opsBelow
    current.left.parent = current
    current.right.parent = current
    return current

#Implements the helper function
def make_full_tree():
    head = Node(0, 0)
    head = full_tree_helper(head)
    return head


#Creates a number of trees equal to the population size, half being full type trees and the other being grow type trees.
def make_pop():
    population = [None] * popSize
    for i in range(0, round(popSize/2)):
        population[i] = make_full_tree()
        population[i].fitness = fitness(population[i])
        population[i+round(popSize/2)] = make_tree()
        population[i+round(popSize/2)].fitness = fitness(population[i])
    return population

#The division operator that avoids division by 0. If the denominator is 0, it instead evaluates the operator to be 1.
def safe_divide(a, b):
    if b == 0:
        return 1
    return a/b

#This is the mutation operation on the tree. It goes through the tree, and for each node, with odds at the set pointrate, it performs a bitflip, replacing a leaf with a random leaf or the operator with a random operator.
def point_mutate(tree):
    if(random.random() < pointRate):
        if tree.type == 1:
            tree.val = random.choice(Leaves)
        else:
            tree.val = random.choice(Operators)
    if tree.left != None:
        point_mutate(tree.left)
    if tree.right != None:
        point_mutate(tree.right)
    return tree

#Used for crossovers. This creates a copy of a subtree from a node that can be spliced so that the original won't be altered.
def copy_from_node(base):
    ops = base.opsBelow
    leaves = base.leavesBelow
    copy = copy_only_node(base)
    copy.opsBelow = ops
    copy.leavesBelow = leaves
    if base.left != None:
        copy.left = copy_from_node(base.left)
        copy.left.parent = copy
    if base.right != None:
        copy.right = copy_from_node(base.right)
        copy.right.parent = copy
    return copy

#Used as a helper function for copy_from_node. Provides a copy of a given node.
def copy_only_node(base):
    copy = Node(base.type, base.depth)
    copy.val = base.val
    copy.fitness = base.fitness
    copy.opsBelow = 1 - base.type
    copy.leavesBelow = base.type
    return copy

#I'm no longer using this crossover algorithm, but I worked hard on it and I think that it's worth showing. It basically goes through the common region of two trees
#and randomly splices each node in it.

#def crossover(p1, p2):
#    if random.random() < .5:
#         if p1.type != p2.type:
#             mix = copy_from_node(p1)
#         else:
#             mix = copy_only_node(p1)
#    else:
#        if p1.type != p2.type:
#            mix = copy_from_node(p2)
#        else:
#            mix = copy_only_node(p2)
#    if p1.type == p2.type and p1.type == 0:
#        mix.left = crossover(p1.left, p2.left)
#        mix.right = crossover(p1.right, p2.right)
#        mix.leavesBelow += mix.left.leavesBelow + mix.right.leavesBelow
#       mix.opsBelow += mix.left.opsBelow + mix.right.opsBelow
#        mix.left.parent = mix
#        mix.right.parent = mix
#    return mix

#Implements a single crossover operation. It uses the selection algorithm to find 2 members to crossover, and applies the operation on them
def run_crossover(pop):
    return subtree_crossover(select_tournament(pop), select_tournament(pop))
    #return crossover(select_tournament(pop), select_tournament(pop))


#Crossover algorithm
def subtree_crossover(p1, p2):
    #Constructs copies of the trees so that they won't be altered
    fake1 = copy_from_node(p1)
    fake2 = copy_from_node(p2)

    #Finds the crossover point for each tree
    branch1 = random_op_node(fake1)
    branch2 = random_op_node(fake2)

    #randomly decides how to splice one branch onto the other tree
    if random.random() < .5:
        if random.random() < .5:
            branch1.left = branch2.left
        else:
            branch1.left = branch2.right
    else:
        if random.random() < .5:
            branch1.right = branch2.right
        else:
            branch1.right = branch2.left

    #Makes sure that the calculations for each node as for how many operators it has as children are accurate
    prop_tree(branch1)
    return fake1

#For a given node, calculates how many operators are children of it, assuming that all nodes below it have accurate operator counts
def recalculate_op_node(node):
    node.opsBelow = 1 + node.left.opsBelow + node.right.opsBelow

#Recursively applies the above function throughout the ancestors of a given node
def prop_tree(node):
    below = node.opsBelow
    recalculate_op_node(node)
    #If this node was accurate, all of its parents will be as well, so we don't need to do the work
    if below == node.opsBelow:
        return
    if node.parent != None:
        prop_tree(node.parent)

#Finds a random node in a tree that happens to be an operator. This is essentially uniform randomness, each operator should have equivalent odds of being chosen
def random_op_node(pop):
    if pop.opsBelow == 1:
        return pop
    num = random.randint(1, pop.opsBelow)
    if num == pop.opsBelow:
        return pop
    elif num <= pop.left.opsBelow:
        return random_op_node(pop.left)
    else:
        return random_op_node(pop.right)

#Calculates the fitness of a tree. This is a recursive algorithm, and it parses the tree back and performs the operations that it finds.
def calculate_tree(tree, variable):
    if tree.type == 1:
        if(tree.val == '1'):
            return 1
        if(tree.val == '2'):
            return 2
        if(tree.val == 'x'):
            return variable
        else:
            return 0
    else:
        if tree.val == '+':
            return (calculate_tree(tree.left, variable) + calculate_tree(tree.right, variable))
        if tree.val == '*':
            return (calculate_tree(tree.left, variable) * calculate_tree(tree.right, variable))
        if tree.val == '-':
            return (calculate_tree(tree.left, variable) - calculate_tree(tree.right, variable))
        if tree.val == '/':
            return safe_divide(calculate_tree(tree.left, variable), calculate_tree(tree.right, variable))   

#Calculates the fitness of a given node by running the calculation on each of the test points.
def fitness(tree):
    val = 0
    var = None
    for i in range(0, pointComparisons):
        val += abs(calculate_tree(tree, testPoints[i]) - eq(testPoints[i]))
    return val


#Returns the fittest tree in a collection of provided trees. This is done by examining the fitness of each tree, and using a simple algorithm to retain only the best at each step
def tournament(values):
    bestFit = float("inf")
    bestTree = None
    for i in range(0, len(values)):
        fit = values[i].fitness
        if fit < bestFit:
            bestFit = fit
            bestTree = values[i]
    return bestTree

#Takes in a population, and outputs the results of a tournament conducted among tornSize random members of the population
def select_tournament(values):
    return tournament(random.sample(values, tornSize))


#Takes in the current generation and outputs the next generation. For each member created in the new generation, there is a 90% chance it was created by crossover, 9% chance it was copied, and a 1% chance that it was mutated
def nextGen(oldGen):
    gen2 = [None] * popSize
    for i in range(0, popSize):
        rng = random.random()
        if rng < .9:
            gen2[i] = run_crossover(oldGen)
        elif rng < .99:
            gen2[i] = select_tournament(oldGen)
        else:
            gen2[i] = point_mutate(copy_from_node(select_tournament(oldGen)))
        gen2[i].fitness = fitness(gen2[i])

        #To prevent bloat prevents trees from being too deep and containing too many leaf nodes. This ensures that trees that are too large won't be selected for reproduction
        if gen2[i].leavesBelow > pow(2, 10):
            gen2[i].fitness = 0
    return gen2

if __name__ == "__main__":
    population = [None] * popSize
    population = make_pop()
    gen = 0
    genFit = None
    print("Initial population seeded")
    while(gen < numGens):
        population = nextGen(population)
        gen+=1
        print("Gen ", gen, " of ", numGens, " complete")
        genFit = fitness(tournament(population))
        if genFit < .1 or gen == numGens: #Halts the algorithm if it reaches a very close approximation.
            break;
        print("Error of gen ", gen, " is ", genFit)
    result = tournament(population)

    print("The algorithm terminated at generation ", gen, " with an error of ", genFit)
    print("The resulting approximation is:")
    
    result.display()
    print()
    
