# genetic-algorithm
I constructed a genetic algorithm. First, I'd like to cite the usage of A Field Guide to Genetic Programming, by Riccardo Poli William Langdon, and Nicholas McPhee.
I made heavy usage of the book to guide me on what genetic algorithms were. I didn't look at any of the actual pseudocode algorithms in the book, nor the chapter which implements a genetic program in Java.
I did use the explanations that they used that the pseudocode and code must be based off of.


My project has within it a function defined to be Eq. Whatever one variable equation is within that is what the program tries to approximate within the range of -1 to 1. The current equation that I'm evaluating is e^x, but you can test it
with others. I do ask you to not include any equations that can run into 0 division errors in this range, since there is a chance that a problematic value will be chosen. Of course, this chance is near 0 (I hope? I don't know how good the
randomization in python is), so maybe it doesn't matter. It has pretty good approximations of quadratic functions such as x^2 + x + 1, and not so great approximations of transcendental functions, such as e^x.

This code is run with a population size of 500 and 50 generations. Feel free to increase those values if you want very slightly more accurate results at the cost of a moderate increase in runtime.

The approximations are done with constructed trees. The possible constants/variables that can be used in these trees are x, 1, 2, and 0. The possible operators are +, -, *, and /. 
In this case, / isn't actually the division operator. It's a protected division operator, which returns 1 if the denominator is 0, and otherwise runs a division.
These trees are initially made through the ramped half-and-half method. All generated trees have a predetermined depth limit, which I chose to be 4 pretty arbitrarily. Half the trees are full trees, which have a full selection of nodes up to this depth.
Every node before the depth limit is an operator, and every node on the depth limit is a termial. The other half of trees are growth trees, in which until one node is constructed at the depth limit, each node has even odds of being
an operator or a leaf. After the depth limit has been reached once, each node constructed must be a leaf until the tree is complete. This allows for a wide variety of possible tree shapes.

The fitness of a tree is calculated by comparing the result of the tree for 100 arbitrary values in the range to the results in the equation. This is stored in the head of the tree upon creation so that this doesn't have to be performed
multiple times for each tree. In my case fitness is essentially error, so the lower the fitness the better.

When seeding the next generation, the population members that are allowed to reproduce are found by conducting tournaments on 20% of the population. So a random 20% of the population is chosen, and the fittest member of that group
gets to leave an offspring. This offspring has a 90% chance of coming about through a crossover mutation, in which case another tournament is conducted to find the other member to breed with. There is a 9% chance of just replicating the parent.
And there is a 1% chance of using point mutation on the offspring.

Crossover:
When two trees are crossed over, first a copy is made of each tree so that the originals won't be impacted if they take part in future tournaments. Then a random operator is found in each tree to be the branching point.
It's randomly determined which branch of the second tree replaces which branch of the first tree at the branching point. Then the first tree with the splice is returned.

Point mutation:
According to the Field Guide, most mutations are actually done by running a crossover operation on a randomly selected tree. I chose to do this method instead in order to understand a different method of doing things, so that I could learn
more than just good ways to reuse old code. This method goes through every node in the tree, and with a rate of 1% performs a bitflip on the node, changing an operator to a different operator or a leaf to a different leaf. Of course, it could
also just change the value of a node to the current value, so the actual mutation rate is .75%.

The program creates new generations, each time reporting the error of the most accurate member of the generation. It stops once it reaches the generation limit, or if the error is very close to 0. Then it outputs what it's best approximation of the function is.


To run the program just run it. If you want to test it out with various equations instead of exp(x), just change the equation in def Eq, which is the first function defined.
