# DatastructureImplementation-Bplustree-ExtendibleHash
Overview

This project implements a B+ Tree and an Extendible Hash data structure in Python. Both structures support efficient insertion, search, and storage handling, making them suitable for large datasets and database systems.

Features

B+ Tree:

Supports insertion, search, and visualization of the tree structure.

Internal nodes guide searches, while leaf nodes store key-value pairs.

Implements node splitting for both leaf and internal nodes when full.

Supports file loading of integers for bulk insertion.

Visualizes the tree with clear internal and child node relationships.

Extendible Hash with disk persistance:

Uses a directory of buckets for dynamic resizing.

Buckets split when full, doubling the directory size if needed.

Supports key-value insertion and unique key enforcement.

Saves and loads bucket data from disk using pickle for persistence.

File Structure

Bplustree.py: B+ Tree implementation with search, insert, node splitting, and visualization.

extendible_hash.py: Extendible hash implementation with bucket splitting and persistence.

How to Run

B+ Tree

python Bplustree.py <filename>

<filename>: A file containing integers, one per line.

The tree will display its structure after all numbers are inserted.

Extendible Hash

python extendible_hash.py

Interactively supports insertion and lookup.

Example Output

B+ Tree Visualization

I[10, 20]
 Child-0: L[5, 7]
 Child-1: L[10, 15]
 Child-2: L[20, 25]

Extendible Hash Example

Insert: (5, 'value1')
Insert: (10, 'value2')
Bucket split triggered!

Future Improvements

Enhance error handling for file reading.

Support deletion in B+ Tree.

Implement rehashing for Extendible Hash.

Add performance benchmarking.

Contributing

Feel free to fork the repo, make improvements, and create a pull request.



This project is licensed under the MIT License.

