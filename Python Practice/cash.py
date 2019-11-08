from cs50 import get_float
from math import floor


def main():
    while True:
    # get user input for change owed
        total_owed = get_float("Change owed: ")
     # round the change to the nearest 100
        coins_owed = floor(total_owed * 100)
    # non-negative value, re-prompt the user
        if coins_owed > 0:
            break
# Assign value to quaters, dimes, nickels, and penny
    quarter = coins_owed // 25
    dime = (coins_owed % 25) // 10
    nickel = ((coins_owed % 25) % 10) // 5
    penny = ((coins_owed % 25) % 10) % 5

    print(f"{quarter + dime + nickel + penny}")


if __name__ == '__main__':

    main()
