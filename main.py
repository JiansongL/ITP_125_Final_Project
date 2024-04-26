import hashlib
import time

# Function to read hashed passwords from a file
def read_hashes(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

# Function to generate MD5 hash of a string
def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

# Function to crack MD5 hashed passwords
def crack_passwords(filename):
    hashed_passwords = read_hashes(filename)
    for password_length in range(1, 7):  # Assume maximum password length of 6 characters
        start_time = time.time()
        found_password = False
        for password in generate_passwords(password_length):
            hashed_password = md5_hash(password)
            if hashed_password in hashed_passwords:
                end_time = time.time()
                print(f"Password: {password}\tTime taken: {end_time - start_time} seconds")
                found_password = True
                break
        if not found_password:
            print(f"No password found for length {password_length}")

# Function to generate all possible passwords of given length
def generate_passwords(length):
    import itertools
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'  # You can add more characters if needed
    for password in itertools.product(chars, repeat=length):
        yield ''.join(password)

# Main function
if __name__ == "__main__":
    crack_passwords("hashes.txt")
