from plugin import plugin, complete
import hashlib
import os


@complete("hash")
@plugin("hash")
def hash_data(ally, s: str) -> None:
    """
    Hashes a given string or file using the specified hash function.

    Parameters:
    ally (obj): Ally assistant object
    s (str): Not used in this function

    Returns:
    None

    Example Usage:
    hash
    """

    def hash_string(user_input, hash_func):
        h = hash_func()
        h.update(user_input.encode())
        return h.hexdigest()

    def hash_file(file_path, hash_func):
        h = hash_func()
        try:
            with open(file_path, 'rb') as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    h.update(chunk)
            return h.hexdigest()
        except IOError:
            return "Error: File not found or inaccessible."

    # Ask user for input type
    input_type = ally.input("Do you want to hash a string or a file? "
                              "(Enter 'string' or 'file'): ").lower()

    # Ask user for hash function
    hash_function = ally.input("Enter the hash function "
                                 "(md5, sha1, sha256, etc.): ").lower()

    try:
        hash_func = getattr(hashlib, hash_function)
    except AttributeError:
        ally.say(f"Invalid hash function: {hash_function}")
        return

    # Perform hashing based on the input type
    if input_type == "string":
        user_input = ally.input("Enter the string to hash: ")
        ally.say("Hashed result: " + hash_string(user_input, hash_func))
    elif input_type == "file":
        file_path = ally.input("Enter the path to the file: ")
        ally.say("Hashed result: " + hash_file(file_path, hash_func))
    else:
        ally.say("Invalid input type. Please enter 'string' or 'file'.")
