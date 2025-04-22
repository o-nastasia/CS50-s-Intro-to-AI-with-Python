import sys

import random

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        

        for var in self.domains:
            for word in list(self.domains[var]):
                if len(word) != var.length:
                    self.domains[var].remove(word)
        
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        
        neighbors_x = self.crossword.neighbors(x)

        if y not in neighbors_x:
            return revised
        
        delete = []
        save = []
        i = self.crossword.overlaps[x, y][0]
        j = self.crossword.overlaps[x, y][1]

        for item in list(self.domains[y]):
            for word in list(self.domains[x]):
                if word[i] != item[j]:
                    delete.append(word)
                else:
                    save.append(word)

        if delete:
            for each in list(delete):
                    if each in save:
                        delete.remove(each)

        if delete:
            for any in list(delete):
                if any in list(self.domains[x]):
                    self.domains[x].remove(any)
            revised = True
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        queue = []
        if arcs:
            queue = arcs
        if arcs == None:
            vars = []
            for var in self.domains:
                if var not in vars:
                    vars.append(var)

            x_count = 0
            y_count = 0
            while x_count < len(vars):
                x = vars[x_count]
                while y_count < len(vars):
                    y = vars[y_count]
                    if x != y:
                        queue.append((x, y))
                    y_count +=1
                x_count += 1
                y_count = 0

        while queue:
            for x, y in queue:
                if self.revise(x, y) == True:
                    if len(self.domains[x]) == 0:
                        return False

                    neighbors = self.crossword.neighbors(x)
                    neighbors.remove(y)
                    for z in neighbors:
                        queue.append((z, x))
                queue.remove((x, y))
        
        return True
            

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var not in assignment:
                return False
        
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for var in assignment:
            neighbors = self.crossword.neighbors(var)
            if neighbors:
                for neighbor in neighbors:
                    if neighbor in assignment:
                        i = self.crossword.overlaps[var, neighbor][0]
                        j = self.crossword.overlaps[var, neighbor][1]
                        if assignment[var][i] != assignment[neighbor][j]:
                            return False
            if len(assignment[var]) != var.length:
                return False
        
        return True
    
    
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        values = dict()
        for key in self.domains[var]:
            values[key] = 0

        neighbors = self.crossword.neighbors(var)
        
        for neighbor in list(neighbors):
            if neighbor in assignment:
                neighbors.remove(neighbor)

        if len(neighbors) == 0:
            return self.domains[var]
        
        for neighbor in neighbors:
            i = self.crossword.overlaps[var, neighbor][0]
            j = self.crossword.overlaps[var, neighbor][1]
            for word in self.domains[var]:
                for item in self.domains[neighbor]:
                    if word[i] != item[j]:
                        values[word] += 1
        
        
        sort = dict()
        for any in values:
            sort.update({values[any]: any})
        
        values = dict(sorted(sort.items()))
        
        outcome = []
        for val in values:
            outcome.append(values[val])
        
        return outcome
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        possible = dict()

        for key in self.domains:
            if key not in assignment:
                possible[key] = self.domains[key]


        count = []
        
        possible_count = dict()
        for item in possible:
            length = len(possible[item])
            possible_count[item] = length
            count.append(length)

        count.sort()
        min = count[0]

        for item in list(possible_count):
            if possible_count[item] > min:
                del possible_count[item]
        
        
        varients = []
        for varient in possible_count:
            varients.append(varient)
        
        if len(varients) == 1:
            return varients[0]
        
        count_degree = []
        for some in list(possible_count):
            neighbors = self.crossword.neighbors(some)
            degree = len(neighbors)
            possible_count[some] = degree
            count_degree.append(degree)
        

        count_degree.sort()
        max = count_degree[-1]
        
    
        for some in list(possible_count):
            if possible_count[some] < max:
                del possible_count[some]
        
        
        var_degree = []
        for key in possible_count:
            var_degree.append(key)

        return random.choice(var_degree)
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        while self.assignment_complete(assignment) != True:
            variable = self.select_unassigned_variable(assignment)
            dom = []
            for word in self.order_domain_values(variable, assignment):
                dom.append(word)
            if len(dom) == 0:
                break
            if len(dom) != 0:
                assignment[variable] = random.choice(dom)
            self.ac3(arcs=None)

        if self.assignment_complete(assignment) == True:
            if self.consistent(assignment) == True:
                return assignment

        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
