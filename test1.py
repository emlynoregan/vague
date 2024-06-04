from vague import vague

def test_vague():
    numbers = vague("Create a list of numbers from 1 to 500. Print the list before returning it.")

    print (1)
    result = vague("Reverse the list of numbers. Print the result before returning it.")

    print (2)
    sum = 0
    for ix, number in enumerate(vague("only the even numbers in the list")):
        print(f"Index: {ix}, Number: {number}")
        # vague(f"Print the index and the number in a nice format.")
        sum = vague('return the sum plus the number, print it first') #(f"sum plus the number. Print the number and the new sum.")
    
    sum1 = vague(f"Print and return the final sum.")

    print(f"Double check...")

    sum2 = vague(f"Sum the even numbers in the list and print the result before returning it.")

    vague(f"check that sum1 == sum2, and raise an exception if that fails.") 

if __name__ == "__main__":
    test_vague()