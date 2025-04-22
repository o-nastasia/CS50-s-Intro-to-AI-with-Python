import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mines = set()
        cells_num = len(self.cells)
        if cells_num == self.count and cells_num != 0:
            for cell in self.cells:
                mines.add(cell)
        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safes = set()
        if self.count == 0:
            for cell in self.cells:
                safes.add(cell)
        return safes
    
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        for entity in list(self.cells):
            if entity == cell:
                self.cells.remove(entity)
                if self.count > 0:
                    self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        for entity in list(self.cells):
            if entity == cell:
                self.cells.remove(entity)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
    
    def neighbors(self, cell):
        neighbors = set()
        i = cell[0]
        j = cell[1]
        if 0 < i < self.height-1 and 0 < j < self.width-1:
            for a in range(i-1, i+2):
                for b in range(j-1, j+2):
                    neighbors.add((a, b))
        elif i == 0 and j == 0:
            for a in range(0, i+2):
                for b in range(0, j+2):
                    neighbors.add((a ,b))
        elif i == self.height-1 and j == self.width-1:
            for a in range(i-1, self.height):
                for b in range(j-1, self.width):
                    neighbors.add((a, b))
        elif i == 0 and j == self.width-1:
            for a in range(0, i+2):
                for b in range(j-1, self.width):
                    neighbors.add((a ,b))
        elif i == self.height-1 and j == 0:
            for a in range(i-1, self.height):
                for b in range(0, j+2):
                    neighbors.add((a, b))
        elif i == 0 and 0 < j < self.width-1:
            for a in range(0, i+2):
                for b in range(j-1, j+2):
                    neighbors.add((a ,b))
        elif i == self.height-1 and 0 < j < self.width-1:
            for a in range(i-1, self.height):
                for b in range(j-1, j+2):
                    neighbors.add((a, b))
        elif 0 < i < self.height-1 and j == 0:
            for a in range(i-1, i+2):
                for b in range(0, j+2):
                    neighbors.add((a ,b))
        elif 0 < i < self.height-1 and j == self.width-1:
            for a in range(i-1, i+2):
                for b in range(j-1, self.width):
                    neighbors.add((a, b))
        neighbors.remove((i,j))
        return(neighbors)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        neighbors = self.neighbors(cell)

        new_sentence = Sentence(neighbors, count)
        new_sentence.count = count

        for entity in list(new_sentence.cells):
            if entity in self.safes:
                new_sentence.mark_safe(entity)
            elif entity in self.mines:
                new_sentence.mark_mine(entity)

        self.knowledge.append(new_sentence)

        safe_update = new_sentence.known_safes()
        mine_update = new_sentence.known_mines()

        if len(safe_update) > 0:
            for s in safe_update:
                self.mark_safe(s)
        if len(mine_update) > 0:
            for m in mine_update:
                self.mark_mine(m)
        i = 0
        while i < len(self.knowledge):
            print(self.knowledge[i].cells, '=', self.knowledge[i].count)
            i += 1

        i = 0
        while i < len(self.knowledge):
            if (len(self.knowledge[i].cells) == self.knowledge[i].count != 0):
                for object in list(self.knowledge[i].cells):
                    if object not in self.mines:
                        self.mark_mine(object)
                self.knowledge[i].count = 0
                self.knowledge[i].cell = set()
            i += 1

        count = len(self.knowledge)
        base = self.knowledge
        i = 0
        while i < count:
            j = 0
            while j < count:
                if len(base[j].cells) < len(base[i].cells) and set(list(base[j].cells)).issubset(list(base[i].cells)) == True:
                    self.knowledge[j].cells = base[j].cells
                    for word in list(base[j].cells):
                        self.knowledge[i].cells.remove(word)
                    new_count = self.knowledge[i].count - self.knowledge[j].count
                    self.knowledge[j].count = self.knowledge[i].count - new_count
                    self.knowledge[i].count = new_count
                    mines = self.knowledge[j].known_mines()
                    for mine in mines:
                        self.mark_mine(mine)
                    safes = self.knowledge[j].known_safes()
                    for safe in safes:
                        self.mark_safe(safe)
                    mines = self.knowledge[i].known_mines()
                    for mine in mines:
                        self.mark_mine(mine)
                    safes = self.knowledge[i].known_safes()
                    for safe in safes:
                        self.mark_safe(safe)
                j += 1
            i += 1
        
        empty = Sentence(set(), 0)
        self.knowledge[:] = [x for x in self.knowledge if x != empty]


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        safes = []

        for k in self.safes:
            safes.append((k))

        for any in list(safes):
            for one in self.moves_made:
                if any == one:
                    safes.remove(any)
        if len(safes) == 0:
            return None
        else:
            move = random.choice(safes)
            print('All safe moves', safes)
            print('Random safe move', move)
            return move


                

    def make_random_move(self):

        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        moves_made = self.moves_made
        all_moves = []
        mines = self.mines


        for i in range(0, self.height):
            for j in range(0, self.width):
                all_moves.append((i,j))
        
        for q in list(all_moves):
            for w in moves_made:
                if q == w:
                    all_moves.remove(q)

        for e in list(all_moves):
            for r in mines:
                if e == r:
                    all_moves.remove(e)
        print ('all_moves:', all_moves)
        move = random.choice(all_moves)
        print ('random move:', move)
        return move