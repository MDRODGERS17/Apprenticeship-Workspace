from cs50 import get_int

while True:
    # Prompts for height
    height = get_int("Height: ")

    # Reprompts for height if positive number 1-8 isn't inserted
    if height >= 1 and height <= 8:
        break

# Iterates through each row
for i in range(height):
    # Prints spaces
    print(" " * (height - i - 1), end="")
    # Prints #
    print("#" * (i + 1))
