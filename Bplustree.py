class Node:
    """
    Base class for both Internal and Leaf nodes in a B+ Tree.
    """
    def __init__(self, is_leaf_node=False):
        self.is_leaf_node = is_leaf_node  
        self.keys = []  
        self.parent = None  # Pointer to parent node

    def is_full(self):
        return len(self.keys) >= 4  # This is as maximum capacity of a node is 4 keys


class Internal(Node):
    """
    This is for Internal node in a B+ Tree, responsible for directing search queries
    and directing to proper leaf page.
    """
    def __init__(self):
        super().__init__(is_leaf_node=False)
        self.children = []  # This will store child pointers
    
    def insert_key(self, key, left_child, right_child):
        """
        This inds the appropriate position to insert key and also makes sure to
        update child pointers accordingly.
        """
        position = 0
        while position < len(self.keys) and key > self.keys[position]:
            position += 1

        self.keys.insert(position, key)

        if position < len(self.children):
            self.children[position] = left_child
            self.children.insert(position + 1, right_child)
        else:
            self.children.append(left_child)
            self.children.append(right_child)

        left_child.parent = self
        right_child.parent = self


class Leaf(Node):
    """
    This is for the leaf node in a B+ Tree. It stores key-value pairs.
    """
    def __init__(self):
        super().__init__(is_leaf_node=True)
        self.values = []  
        self.pointer = None  # This is ointer to the next leaf node which helps with range queries
    
    def insert_key_and_value(self, key, value):
        """
        It inserts a key-value pair in sorted order, avoiding duplicates
        and allowing unique keys only. It returns False if key already exists 
        and True if insertion was successful.
        """
        position = 0
        while position < len(self.keys) and key > self.keys[position]:
            position += 1

        if position < len(self.keys) and self.keys[position] == key:
            return False  # Key already exists, so insertion fails
            
        self.keys.insert(position, key)
        self.values.insert(position, value)
        return True


class BPlusTree:
    """
    B+ Tree structure that supports features such as
    search and insert.
    """
    def __init__(self):
        self.root = Leaf()  # At the start, the root is a leaf node
        self.leaf_num = 1  # Counts number of  leaf nodes
    
    def search(self, key):
        """
        This function searches for a key and returns the associated value if found.
        """
        node = self.root
        while not node.is_leaf_node:  # This traverses until a leaf node is found
            position = 0
            while position < len(node.keys) and key >= node.keys[position]:
                position += 1
            node = node.children[position]

        for i, j in enumerate(node.keys):
            if j == key:
                return node.values[i]  

        return None  # If key is not found
    
    def insert(self, key, value=None, display=False):
        """
        Inserts a key-value pair into the tree.
        """
        if value is None:
            value = key  # Use the key as value if no value is provided
        
        if len(self.root.keys) == 0:
            self.root.keys.append(key)
            self.root.values.append(value)
            if display:
                print(f"Inserted: {key}")
            return True

        node = self.root
        while not node.is_leaf_node:
            position = 0
            while position < len(node.keys) and key >= node.keys[position]:
                position += 1
            node = node.children[position]

        insert_done = node.insert_key_and_value(key, value)
        if not insert_done:
            return False  # Key already exists, so insertion fails
        
        if node.is_full():
            self.split_node(node)  # Split the node if it's full
        if display:
            print(f"Inserted: {key}")
        
        return True
    
    def split_node(self, node):
        """
        When the node is full, it splits a full node and rearranges values and 
        updates the tree structure.
        """
        if node.is_leaf_node:
            new_node = Leaf()
            self.leaf_num += 1

            mid = len(node.keys) // 2
            new_node.keys = node.keys[mid:]
            new_node.values = node.values[mid:]
            node.keys = node.keys[:mid]
            node.values = node.values[:mid]

            new_node.pointer = node.pointer  # Makes sure leaf nodes are linked to each other 
            node.pointer = new_node

            copied_or_pushed_key = new_node.keys[0]  # Promotes the first key of new node
        else:
            new_node = Internal()

            mid = len(node.keys) // 2
            copied_or_pushed_key = node.keys[mid]  # Middle key moves up

            new_node.keys = node.keys[mid+1:]
            node.keys = node.keys[:mid]

            new_node.children = node.children[mid+1:]
            node.children = node.children[:mid+1]

            for child in new_node.children:
                child.parent = new_node

        if node.parent is None:
            new_root = Internal()
            new_root.keys.append(copied_or_pushed_key)
            new_root.children.append(node)
            new_root.children.append(new_node)
            node.parent = new_root
            new_node.parent = new_root
            self.root = new_root  # Update root
        else:
            parent = node.parent
            position = parent.children.index(node)
            parent.keys.insert(position, copied_or_pushed_key)
            parent.children.insert(position + 1, new_node)
            new_node.parent = parent

            if len(parent.keys) > 4:
                self.split_node(parent)  # Allows to recursively split parent node if needed

    def load_from_file(self, filename):
        """
        Reads integers from a file and inserts them into the data structure.
        """
        try:
            with open(filename, 'r') as file:
                for line in file:
                    number = int(line.strip())  # Convert each line to an integer
                    self.insert(number, display=True)  # Insert into your structure with display=True to help with large dataset
        except FileNotFoundError:
            print(f"Error: {filename} was not found.")
        except ValueError:
            print(f"Error: Invalid value found in {filename}")
    def visualize(self, node=None, level=0, result=None):
        """
        Generates a string representation of the B+ Tree with clearer internal-child relationships.
        """
        if result is None:
            result = []

        if node is None:
            node = self.root

        if len(result) <= level:
            result.append([])

        if node.is_leaf_node:
            node_str = f"L{node.keys}"  
        else:
            node_str = f"I{node.keys}"  #internal node keys

        # Add the current node's string representation at the current level
        result[level].append(node_str)

        if not node.is_leaf_node:
            # If it's an internal node, it allows to show connection to children
            for idx, child in enumerate(node.children):
                child_str = f"Child-{idx}: " + ("L" if child.is_leaf_node else "I") + str(child.keys)
                result[level].append(child_str)
                # Helps visualize the child nodes using recursion
                self.visualize(child, level + 1, result)

        if level == 0:
            output = ""
            for level_nodes in result:
                output += "\n ".join(level_nodes) + "\n"
            return output

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python Bplustree.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]  # Get filename from command-line argument

    bplus_tree = BPlusTree()  
    bplus_tree.load_from_file(filename)  # Load numbers from the file
    print(bplus_tree.visualize())  # Print the B+ Tree structure after insertions
