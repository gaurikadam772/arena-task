
# Student Grade Calculator

# Function to calculate grade and message
def calculate_grade(marks):

    if marks >= 90:
        grade = "A"
        message = "Excellent! Outstanding performance! 🌟"

    elif marks >= 80:
        grade = "B"
        message = "Very Good! Keep it up! 👍"

    elif marks >= 70:
        grade = "C"
        message = "Good Job! You can do even better! 😊"

    elif marks >= 60:
        grade = "D"
        message = "Keep practicing! Improvement is possible! 💪"

    else:
        grade = "F"
        message = "Don't give up! Keep learning and try again! ❤️"

    return grade, message


# Function to get valid marks
def get_valid_marks():

    while True:
        try:
            marks = float(input("Enter marks (0-100): "))

            if 0 <= marks <= 100:
                return marks

            else:
                print("Invalid marks! Enter marks between 0 and 100.")

        except ValueError:
            print("Invalid input! Please enter a number.")


# Main program
def main():

    print("================================")
    print("     STUDENT GRADE CALCULATOR")
    print("================================")

    student_name = input("Enter student name: ").strip()

    while not student_name:
        print("Name cannot be empty!")
        student_name = input("Enter student name: ").strip()

    marks = get_valid_marks()

    grade, message = calculate_grade(marks)

    print("\n📊 RESULT FOR", student_name.upper())
    print("--------------------------------")
    print(f"Marks: {marks:g}/100")
    print(f"Grade: {grade}")
    print(f"Message: {message}")
    print("--------------------------------")

    print("Thank you for using Grade Calculator!")


# Run the program
if __name__ == "__main__":
    main()
