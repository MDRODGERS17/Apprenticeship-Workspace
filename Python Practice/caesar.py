import sys
from cs50 import get_string


def main():
    # Checks for CLA and prints error message along with system exit of 1
    if len(sys.argv) != 2:
        print("Usage: My name is Maximus Decimus Meridius, Commander of the Armies of the North.")
        sys.exit(1)
    # Prompts for ptext and prints out ciphertext
    q = int(sys.argv[1])
    plaintext = get_string("plaintext: ")

    print("ciphertext: ", end="")
    # Checks ptext to ensure only letters
    for ch in plaintext:
        if not ch.isalpha():
            print(ch, end="")

        # Capitalizes upper and lower
        ascii_offset = 65 if ch.isupper() else 97

        pt = ord(ch) - ascii_offset
        ct = (pt + q) % 26
        # Executes and gets rid of newline
        print(chr(ct + ascii_offset), end="")

    print()

    return 0


if __name__ == "__main__":
    main()
