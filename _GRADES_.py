import json
import os

DATA_FILE = "courses_data.json"

class Section:
    def __init__(self, name, weight, grades=None):
        self.name = name
        self.weight = weight
        self.grades = grades if grades is not None else []

    def add_grade(self, grade):
        self.grades.append(grade)

    def average(self):
        if self.grades:
            return sum(self.grades) / len(self.grades)
        return 0.0

    def to_dict(self):
        return {"name": self.name, "weight": self.weight, "grades": self.grades}

    @staticmethod
    def from_dict(data):
        return Section(data["name"], data["weight"], data.get("grades", []))

    def __str__(self):
        avg = self.average()
        return f"{self.name}: Weight = {self.weight}%, Average = {avg:.2f}, Grades = {self.grades}"

class Course:
    def __init__(self, name, sections=None):
        self.name = name
        self.sections = sections if sections is not None else {}

    def add_section(self, name, weight):
        if name in self.sections:
            print(f"Section '{name}' already exists in {self.name}. Updating its weight to {weight}%.")
            self.sections[name].weight = weight
        else:
            self.sections[name] = Section(name, weight)

    def add_assignment_grade(self, section_name, grade):
        if section_name in self.sections:
            self.sections[section_name].add_grade(grade)
        else:
            print(f"Section '{section_name}' does not exist in {self.name}.")

    def update_section_weight(self, section_name, new_weight):
        if section_name in self.sections:
            self.sections[section_name].weight = new_weight
        else:
            print(f"Section '{section_name}' does not exist in {self.name}.")

    def calculate_overall_grade(self):
        overall = 0.0
        for section in self.sections.values():
            overall += section.average() * (section.weight / 100)
        return overall

    def calculate_current_grade(self):
        total_weight = 0.0
        total_score = 0.0
        for section in self.sections.values():
            if section.grades:
                total_score += section.average() * section.weight
                total_weight += section.weight
        if total_weight == 0:
            return None
        return total_score / total_weight

    def determine_letter_grade(self, numeric_grade):
        if numeric_grade >= 90:
            return "A"
        elif numeric_grade >= 80:
            return "B"
        elif numeric_grade >= 70:
            return "C"
        elif numeric_grade >= 60:
            return "D"
        else:
            return "F"

    def display_status(self):
        print(f"\n--- Grading Status for Course: {self.name} ---")
        for section in self.sections.values():
            print(section)
        current_grade = self.calculate_current_grade()
        if current_grade is None:
            print("Grade Achieved So Far: No grades entered yet.")
        else:
            print(f"Grade Achieved So Far: {current_grade:.2f}% ({self.determine_letter_grade(current_grade)})")
        final_grade = self.calculate_overall_grade()
        print(f"Final Grade (if remaining sections score 0): {final_grade:.2f}% ({self.determine_letter_grade(final_grade)})\n")

    def to_dict(self):
        return {"name": self.name, "sections": {name: section.to_dict() for name, section in self.sections.items()}}

    @staticmethod
    def from_dict(data):
        sections = {name: Section.from_dict(sdata) for name, sdata in data.get("sections", {}).items()}
        return Course(data["name"], sections)

class CourseManager:
    def __init__(self):
        self.courses = {}
        self.load_data()

    def add_course(self, course):
        self.courses[course.name] = course
        self.save_data()

    def get_course_by_index(self, index):
        courses = list(self.courses.values())
        if 0 <= index < len(courses):
            return courses[index]
        return None

    def list_courses(self):
        return list(self.courses.keys())

    def save_data(self):
        data = {name: course.to_dict() for name, course in self.courses.items()}
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                for name, course_data in data.items():
                    self.courses[name] = Course.from_dict(course_data)
        else:
            self.courses = {}

def setup_course(course):
    print(f"\nDefine grading sections for course: {course.name}")
    while True:
        section_name = input("Enter section name (or type 'done' to finish): ").strip()
        if section_name.lower() == "done":
            break
        try:
            weight = float(input(f"Enter weight (in percent) for {section_name}: "))
        except ValueError:
            print("Invalid weight, please enter a numeric value.")
            continue
        course.add_section(section_name, weight)
    print(f"Finished setting up course: {course.name}\n")

def course_menu(course, manager):
    while True:
        course.display_status()
        print("Options for course:", course.name)
        print("1. Add assignment grades to a section")
        print("2. Update a section's weight")
        print("3. Add a new section")
        print("4. Return to course selection")
        choice = input("Choose an option (1-4): ").strip()
        if choice == "1":
            if not course.sections:
                print("No sections available. Please add a section first.")
                continue
            sections_list = list(course.sections.keys())
            print("\nAvailable Sections:")
            for idx, sec_name in enumerate(sections_list, start=1):
                print(f"• {sec_name}")
            try:
                selected = int(input("Select a section by number (position in the list): ")) - 1
            except ValueError:
                print("Invalid input. Please enter a number corresponding to the section.")
                continue
            if 0 <= selected < len(sections_list):
                section_name = sections_list[selected]
                while True:
                    grade_input = input(f"Enter assignment grade for '{section_name}' (or type 'done' to finish): ").strip()
                    if grade_input.lower() == "done":
                        break
                    try:
                        grade = float(grade_input)
                    except ValueError:
                        print("Invalid grade. Please enter a numeric value.")
                        continue
                    course.add_assignment_grade(section_name, grade)
                    manager.save_data()
            else:
                print("Invalid section number selected.")
        elif choice == "2":
            section_name = input("Enter the section name to update its weight: ").strip()
            try:
                new_weight = float(input("Enter the new weight (in percent): "))
            except ValueError:
                print("Invalid weight. Please enter a numeric value.")
                continue
            course.update_section_weight(section_name, new_weight)
            manager.save_data()
        elif choice == "3":
            section_name = input("Enter new section name: ").strip()
            try:
                weight = float(input(f"Enter weight (in percent) for {section_name}: "))
            except ValueError:
                print("Invalid weight. Please enter a numeric value.")
                continue
            course.add_section(section_name, weight)
            manager.save_data()
        elif choice == "4":
            break
        else:
            print("Invalid option. Please choose a number between 1 and 4.")

def main_menu():
    manager = CourseManager()
    while True:
        print("\n=== Course Manager ===")
        courses = manager.list_courses()
        if courses:
            print("Available courses:")
            for cname in courses:
                print(f"• {cname}")
        else:
            print("No courses available yet.")
        print("Options:")
        print("1. Select a course")
        print("2. Add a new course")
        print("3. Grades Snapshot")
        print("4. Quit")
        choice = input("Choose an option (1-4): ").strip()
        if choice == "1":
            if not courses:
                print("No courses available. Please add a course first.")
                continue
            try:
                selected = int(input("Enter the course number (position in the list): ")) - 1
            except ValueError:
                print("Invalid input. Please enter a valid course number.")
                continue
            course = manager.get_course_by_index(selected)
            if course:
                course_menu(course, manager)
            else:
                print("Invalid course number selected.")
        elif choice == "2":
            course_name = input("Enter new course name: ").strip()
            if course_name in manager.courses:
                print("Course already exists.")
            else:
                new_course = Course(course_name)
                setup_course(new_course)
                manager.add_course(new_course)
        elif choice == "3":
            print("\n=== Grades Snapshot ===")
            if not courses:
                print("No courses available yet.")
            else:
                for course in manager.courses.values():
                    print(f"\nCourse: {course.name}")
                    current_grade = course.calculate_current_grade()
                    if current_grade is None:
                        print("  Grade Achieved So Far: No grades entered yet.")
                    else:
                        print(f"  Grade Achieved So Far: {current_grade:.2f}% ({course.determine_letter_grade(current_grade)})")
                    final_grade = course.calculate_overall_grade()
                    print(f"  Final Grade (if remaining sections score 0): {final_grade:.2f}% ({course.determine_letter_grade(final_grade)})")
            print("")
        elif choice == "4":
            print("Exiting program. Your data has been saved.")
            break
        else:
            print("Invalid option. Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    main_menu()
