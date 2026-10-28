"""
Personal Introduction Program
Week 1 - Python Basics
"""

def main():
    print("=" * 42)
    print("       PERSONAL INTRODUCTION")
    print("=" * 42)

    name = input("What is your name? ").strip()
    while not name:
        print("Name cannot be empty.")
        name = input("What is your name? ").strip()

    while True:
        age_text = input("How old are you? ").strip()
        try:
            age = int(age_text)
            if age < 0:
                print("Please enter a non-negative age.")
                continue
            break
        except ValueError:
            print("Please enter your age as a whole number.")

    hobby = input("What is your favorite hobby? ").strip()
    if not hobby:
        hobby = "exploring new interests"

    print("\n" + "-" * 42)
    print(f"🎉 Welcome, {name}! 🎉")
    print(f"You are {age} years old and enjoy {hobby}.")
    print("Thanks for introducing yourself!")
    print("-" * 42)


if __name__ == "__main__":
    main()
