# Utilize the GPU
import pyopencl as cl
import numpy as np
import hashlib
import time
import itertools

# Function to read hashed passwords from a file
def read_hashes(filename):
    # Read all lines from the file and strip the newline character
    with open(filename, 'r') as file:
        return [line.strip() for line in file]
    
# Function to generate MD5 hash of a string
def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

# Function to crack MD5 hashed passwords
def crack_passwords(filename):
    # Initialize a list to store the passwords
    passwrd_list = []
    # Read hashed passwords from the file
    hashed_passwords = read_hashes(filename)
    # maximum password length of 6 characters
    for password_length in range(1, len(hashed_passwords) + 1):
        # Start the timer
        start_time = time.time()
        # Iterate over all possible passwords of given length
        found_password = False
        # Generate all possible passwords of given length
        for password in generate_passwords(password_length):
            # add time limit
            if time.time() - start_time > 180:  # Check if the time limit of 3 minutes is exceeded
                print("Time limit exceeded")
                passwrd_list.append("Time limit exceeded")  # Mark the password as "Time limit exceeded"
                break
            # Generate the hash of the password and check if it matches any of the hashed passwords
            hashed_password = md5_hash(password)
            # If the hash is found in the list of hashed passwords, print the password and time taken
            if hashed_password in hashed_passwords:
                # Stop the timer
                end_time = time.time()
                result = f"Password: {password}\tTime taken: {round(end_time - start_time, 3)} seconds"
                # Print the password and time taken
                print(result)
                # Append the password to the list
                passwrd_list.append(result)
                # Set the flag to True to indicate that the password is found
                found_password = True
                break
        # If no password is found for the given length, print a message
        if not found_password:
            print(f"No password found for length {password_length}")
    # Return the list of passwords
    return passwrd_list

# Function to generate all possible passwords of given length
def generate_passwords(length):
    # Define the characters to be used in the password
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    # Generate all possible passwords of given length
    for password in itertools.product(chars, repeat=length):
        yield ''.join(password)

# Create a context and queue
context = cl.create_some_context()
queue = cl.CommandQueue(context)

# Create a buffer to hold the hashed passwords
hashed_passwords = read_hashes('hashed_passwords.txt')
hashed_passwords_np = np.array(hashed_passwords, dtype=np.str)
hashed_passwords_buffer = cl.Buffer(context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=hashed_passwords_np)

# Create a buffer to hold the generated passwords
passwords_np = np.zeros((len(hashed_passwords), 6), dtype=np.uint8)
passwords_buffer = cl.Buffer(context, cl.mem_flags.WRITE_ONLY, passwords_np.nbytes)

# Create a program
program = cl.Program(context, """
    __kernel void generate_passwords(__global uchar* passwords, __global uchar* hashed_passwords) {
        int i = get_global_id(0);
        char chars[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        for (int j = 0; j < 6; j++) {
            passwords[i * 6 + j] = chars[(i >> (5 - j) * 6) & 0x3F];
        }
    }
""").build()

# Execute the program
program.generate_passwords(queue, passwords_np.shape, None, passwords_buffer, hashed_passwords_buffer)

# Read the generated passwords
cl.enqueue_copy(queue, passwords_np, passwords_buffer).wait()

# Crack the passwords
crack_passwords('passwords.txt')
# Function to write the cracked password to a file
def out_file(filename, password_list):
    # Write the password to the file
    with open(filename, 'w') as file:
        # Write the password to the file
        for password in password_list:
            file.write(password + "\n")

# Main function
if __name__ == "__main__":
    # Crack the hashed passwords
    out_file("passwords.txt", crack_passwords("hashes.txt"))