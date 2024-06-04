from vague import vague

def test_vague():
    num_people = vague("""
        usage: python test2.py --num_people <number of people>. 
        use argparse to get the number of people from the command line.
        Print the number of people before returning it.
        Return it as an integer.
""")
    
    people = vague(f"""
    Create a list of people, there should be num_people people in the list.
    They need to be dictionaries with the following keys:
    - name: a string
    - age: an integer
                   
    Generate random ages for the people.
    You should make up a static list of plausible names, then randomly assign names to the people. 
    Some example names: John, Jane, Alice, Bob, Ian, Charlie, David, Emily, Frank, Grace, Henry, Isaac, Jack, Kate, Lily, Mary, Nick, Olivia, Peter, Queen, Rachel, Sam, Tom, Ursula, Victor, Wendy, Xavier, Yvonne, Zach, etc.
                   
    Print the list of people before returning it.
""")
    
    johns_and_jacks = vague("""
        Get the subset of the people, who are named John or Jack. Be permissive with the name, e.g. John, john, JOHN, JoHn, etc,
        also variations that mean the same thing, e.g. Jon, Jonathan, Ian, etc. Note that elements in the list are dictionaries,
        so you need to check the 'name' key in the dictionary.
    """)
    
    vague("""
        Print the johns_and_jacks list before returning it. Say something superlative about each one.
    """)

if __name__ == "__main__":
    test_vague()