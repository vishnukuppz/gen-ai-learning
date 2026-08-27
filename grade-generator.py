# Week 1 - Day 2 Assignemnt: Grade Generator
mark = int(input("Enter your mark: "))

#raise exception if mark is less than 0 or greater than 100
if(mark < 0 or mark > 100):
    raise ValueError("Invalid mark. Please enter a mark between 0 and 100.")


if mark >= 90:
    print("Grade: A")
elif mark >= 80:
    print("Grade: B")
elif mark >= 70:
    print("Grade: C")
elif mark >= 60:    
    print("Grade: D")
else:
    print("Grade: E")