import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import time
import numpy as np

def process_chunk(start_i, end_i, limit):
    """Process a chunk of numbers for the Atkin sieve using NumPy."""
    res = np.zeros(limit + 1, dtype=bool)
    
    # Create arrays for i and j values
    i_range = np.arange(start_i, end_i)
    j_range = np.arange(1, limit + 1)
    
    # Use broadcasting for faster computation
    i_squared = i_range[:, np.newaxis] ** 2
    j_squared = j_range ** 2
    
    # Calculate n values for all combinations of i and j
    n1 = 4 * i_squared + j_squared
    valid1 = (n1 <= limit)
    n1 = n1[valid1]
    mask1 = np.logical_or(n1 % 12 == 1, n1 % 12 == 5)
    res[n1[mask1]] ^= True
    
    n2 = 3 * i_squared + j_squared
    valid2 = (n2 <= limit)
    n2 = n2[valid2]
    mask2 = (n2 % 12 == 7)
    res[n2[mask2]] ^= True
    
    n3 = 3 * i_squared - j_squared
    valid3 = (n3 > 0) & (n3 <= limit)
    n3 = n3[valid3]
    mask3 = (n3 % 12 == 11)
    res[n3[mask3]] ^= True
    
    return res

def parallel_sieve(limit):
    """Generate prime numbers up to the specified limit using parallel processing and NumPy."""
    if limit < 2:
        return np.array([], dtype=bool)
    if limit == 2:
        return np.array([False, True], dtype=bool)
    if limit == 3:
        return np.array([False, True, True], dtype=bool)

    # Initialize the sieve array
    res = np.zeros(limit + 1, dtype=bool)
    res[2] = True
    res[3] = True

    # Determine optimal chunk size based on CPU cores
    num_cores = multiprocessing.cpu_count()
    chunk_size = max(1, int(np.sqrt(limit + 1)) // (num_cores * 2))
    chunks = [(i, min(i + chunk_size, int(np.sqrt(limit + 1)))) 
             for i in range(1, int(np.sqrt(limit + 1)), chunk_size)]

    # Process chunks in parallel
    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = [executor.submit(process_chunk, start, end, limit) 
                  for start, end in chunks]
        results = [future.result() for future in futures]

    # Merge results using NumPy operations
    for chunk_res in results:
        res |= chunk_res

    # Final sieving step
    r = 5
    r_limit = int(np.sqrt(limit))
    while r <= r_limit:
        if res[r]:
            res[r*r::r*r] = False
        r += 1

    return res

def pick_prime(primes, lowest_prime, prime_limit):
    """Pick the first prime number that's >= lowest_prime."""
    prime_indices = np.where(primes[lowest_prime:prime_limit + 1])[0]
    return lowest_prime + prime_indices[0] if len(prime_indices) > 0 else None

def hash_string(string, modulus):
    """Hash a string using the XOR method."""
    hash_value = 5381
    for char in string:
        hash_value = ((hash_value << 5) + hash_value) ^ ord(char)
    return hash_value % modulus

if __name__ == '__main__':
    try:
        start_time = time.time()
        
        # Parameters
        prime_limit = 100000
        lowest_prime = 1000
        
        # Generate primes list using parallel processing
        print("Generating primes...")
        primes = parallel_sieve(prime_limit)
        
        # Get modulus
        modulus = pick_prime(primes, lowest_prime, prime_limit)
        if modulus is None:
            raise ValueError("No suitable prime number found in the specified range")
        
        print(f"Using prime modulus: {modulus}")
        
        # Test strings
        test_array = ["alpha", "beta", "gamma", "delta", "epsilon"]
        
        # Process strings sequentially
        print("Hashing strings...")
        hash_values = [hash_string(s, modulus) for s in test_array]
        
        # Print results
        print("\nResults:")
        for string, hash_value in zip(test_array, hash_values):
            print(f"Hash of '{string}' is {hash_value}")
        
        end_time = time.time()
        print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")