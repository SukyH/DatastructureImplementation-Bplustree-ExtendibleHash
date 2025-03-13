import os
import pickle
import sys

class Bucket:
    """
    This class represents a bucket in the extendible hash table.
    Each bucket has a capacity, local depth and a bucket id.
    """
    def __init__(self, capacity, local_depth=1, bucket_id=None):
        self.capacity = capacity  # Maximum number of items in the bucket
        self.local_depth = local_depth  # Depth to help with matching
        self.items = {}  # Stores key and value pairs
        self.bucket_id = bucket_id  # Bucket id
        
        # If we have a known bucket id, it loads from disk 
        if bucket_id is not None:
            filename = f"bucket{bucket_id}.pkl"
            if os.path.exists(filename):
                try:
                    with open(filename, 'rb') as f:
                        data = pickle.load(f)
                        self.items = data.get('items', {})
                        self.local_depth = data.get('local_depth', local_depth)
                except Exception as e:
                    print(f"Warning: Failed to load bucket {bucket_id}: {e}")

    def insert(self, key, value):
        """Checks if key is unqiue and bucket has space to insert a key-value pair."""
        if key in self.items:
            return False  #to ensure unique keys

        if len(self.items) < self.capacity:
            self.items[key] = value
            self.save()
            return True
        return False  # if bucket is full,insertion will fail

    def save(self):
        """This will save the bucket to disk."""
        if self.bucket_id is not None:
            filename = f"bucket_{self.bucket_id}.pkl"
            try:
                with open(filename, 'wb') as f:
                    pickle.dump({
                        'items': self.items,
                        'local_depth': self.local_depth
                    }, f)
            except Exception as e:
                print(f"Failed to save bucket {self.bucket_id}: {e}")
    
    def __str__(self):
        """Helps with printing out visualization"""
        return f"[LocalDepth: {self.local_depth}, Items: {self.items}]"


class ExtendibleHash:
    """
    Implements an extendible hash table using directory,splitting bucket,
    in-memory and disk storage
    """
    def __init__(self, bucket_capacity=2, global_depth=1):
        self.global_depth = global_depth  # Global depth which tells us directory size
        self.bucket_capacity = bucket_capacity  
        self.directory = [None] * (2 ** self.global_depth)  # To  iitialize directory
        self.next_bucket_id = 0  
        
        # Creates initial bucket and points all  the directory entries to it
        initial_bucket = Bucket(self.bucket_capacity, self.global_depth, self.next_bucket_id)
        self.next_bucket_id += 1
        
        for i in range(len(self.directory)):
            self.directory[i] = initial_bucket

        # Save metadata about the hash table
        self.save_metadata()

    def save_metadata(self):
        """Save metadata about the hash table structure."""
        try:
            with open('hash_metadata.pkl', 'wb') as f:
                pickle.dump({
                    'global_depth': self.global_depth,
                    'next_bucket_id': self.next_bucket_id
                }, f)
        except Exception as e:
            print(f"Warning: Failed to save hash table metadata: {e}")

    def hash_function(self, key):
        """This uses inbuilt hash function to returns a hash value for the given key."""
        return abs(hash(key)) % (2 ** 32)

    def get_directory_index(self, key):
        """This is used to determine the  bucket index using global depth bits """
        mask = (1 << self.global_depth) - 1
        return self.hash_function(key) & mask

    def grow_directory(self):
        """This will doubles the directory size and update pointers."""
        old_size = len(self.directory)
        self.global_depth += 1
        
        # Double the directory
        for i in range(old_size):
            self.directory.append(self.directory[i])
            
        # Save updated metadata
        self.save_metadata()

    def split_bucket(self, index):
        """This will splits a bucket when it becomes full."""
        old_bucket = self.directory[index]
        
        # This checks if we need to grow the directory
        if old_bucket.local_depth >= self.global_depth:
            self.grow_directory()
            # This will recalculate the  index after growing the directory iterating over the keys 
            if old_bucket.items:
                key = next(iter(old_bucket.items.keys()))
                index = self.get_directory_index(key)
        
        
        old_bucket.local_depth += 1
        
        # Create new bucket with the same local depth
        new_bucket = Bucket(self.bucket_capacity, old_bucket.local_depth, self.next_bucket_id)
        self.next_bucket_id += 1
        
        # Update directory pointers based on the new bit which help decide what bucket key-value pair goes into.
        shift = 1 << (old_bucket.local_depth - 1)
        for i in range(len(self.directory)):
            if self.directory[i] is old_bucket and (i & shift) != 0:
                self.directory[i] = new_bucket
        
        # Redistribute items between the buckets
        items_to_redistribute = list(old_bucket.items.items())
        old_bucket.items.clear()
        
        for key, value in items_to_redistribute:
            # Get the correct bucket for this key
            dir_index = self.get_directory_index(key)
            self.directory[dir_index].items[key] = value
        
        # Save both buckets
        old_bucket.save()
        new_bucket.save()
        
        # Save metadata (next_bucket_id changed)
        self.save_metadata()

    def insert(self, key, value):
        """Insert a key-value pair into the hash table."""
        max_attempts = 10  # Prevent infinite recursion
        for attempt in range(max_attempts):
            index = self.get_directory_index(key)
            bucket = self.directory[index]
            
            
            if key in bucket.items:
                return False #again check for duplicates first
            
            #  insert into the bucket
            if bucket.insert(key, value):
                bucket_count = self.count_buckets()
                print(f"Inserted key {key}. Number of buckets: {bucket_count}")
                return True
            
            # If insertion failed, split the bucket and try again
            self.split_bucket(index)
        
        # If we reach here, insertion failed 
        return False

    def search(self, key):
        """This will earch for a key in the hash table."""
        index = self.get_directory_index(key)
        bucket = self.directory[index]
        return bucket.items.get(key)

    def count_buckets(self):
        """Count the number of unique buckets."""
        unique_buckets = set(id(bucket) for bucket in self.directory)
        return len(unique_buckets)

    def print_number_of_buckets(self):
        """Print the number of unique buckets."""
        num_buckets = self.count_buckets()
        print(f"Number of buckets: {num_buckets}")
        return num_buckets

    def load_from_file(self, filename):
        """Load keys from a file and insert them into the hash table."""
        count = 0
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        key = int(line)
                        self.insert(key, key)
                        count += 1
                        if count % 100 == 0:
                            print(f"Processed {count} keys so far...")
                    except ValueError:
                        print(f"Skipping invalid entry: {line}")
            
            print(f"Successfully processed {count} keys from {filename}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            sys.exit(1)

    def visualize(self):
        """Visualize the hash table structure."""
        print(f"Global Depth: {self.global_depth}")
        print("\nDirectory Structure:")
        print("-" * 50)
        
        # Create a mapping of bucket objects to consistent IDs
        bucket_to_id = {}
        for i, bucket in enumerate(self.directory):
            if id(bucket) not in bucket_to_id:
                bucket_to_id[id(bucket)] = bucket.bucket_id
        
        # we first prrint directory entries
        for i in range(len(self.directory)):
            bucket_id = bucket_to_id[id(self.directory[i])]
            print(f"Dir[{i}] -> Bucket-{bucket_id}")
        
        # We then print bucket contents
        print("\nBucket Contents:")
        print("-" * 50)
        
        # To ensure unique buckets
        unique_buckets = {}
        for bucket in self.directory:
            if id(bucket) not in unique_buckets:
                unique_buckets[id(bucket)] = bucket
        
        # Sort buckets by their ID to help print
        sorted_buckets = sorted([(bucket.bucket_id, bucket) for bucket in unique_buckets.values()])
        
        for bucket_id, bucket in sorted_buckets:
            print(f"Bucket-{bucket_id} (Local Depth: {bucket.local_depth}):")
            if not bucket.items:
                print("  Empty")
            else:
                for key, value in sorted(bucket.items.items()):
                    print(f"  Key: {key}, Value: {value}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extendiblehash.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    eh = ExtendibleHash(bucket_capacity=2)
    print(f"Loading data from {filename}...")
    eh.load_from_file(filename)
    print("\nVisualization of the Extendible Hash Table:")
    eh.visualize()
    eh.print_number_of_buckets()


if __name__ == "__main__":
    main()

