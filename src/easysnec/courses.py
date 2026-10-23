from dataclasses import dataclass

@dataclass(frozen=True)
class Course:
    course_name: str
    is_score_o: bool
    stations: list[int]

@dataclass()
class CourseSet:
    name: str
    enabled: bool
    courses: list[Course]



ANIMAL_MAPPING = {
    "Frog": 32,
    "Octopus": 34,
    "Penguin": 38,
    "Sheep": 40,
    "Lion": 31,
    "Dog": 33,
    "Bee": 35,
    "Bird": 36,
    "Elephant": 37,
    "Crab": 39,
}

EMOJI_MAPPING = {
    32: "🐸",
    34: "🐙",
    38: "🐧",
    40: "🐑",
    31: "🦁",
    33: "🐕",
    35: "🐝",
    36: "🐦",
    37: "🐘",
    39: "🦀",
}


class CourseManager():
    course_sets:dict[str, CourseSet] = {}

    def __init__(self):
        # default course set
        self.add_course_set(CourseSet(
            name = "Cambridge Plays Animal-O 10s",
            enabled = True,
            courses = [
                Course("Frog", False, [32, 40, 39, 38, 35, 34, 36, 37, 31, 33]),
                Course("Octopus", False, [34, 36, 39, 40, 32, 33, 37, 38, 31, 35]),
                Course("Penguin", False, [38, 39, 32, 34, 35, 36, 37, 33, 31, 40]),
                Course("Sheep", False, [40, 36, 34, 31, 32, 33, 35, 37, 38, 39]),
            ]
        ))
        self.add_course_set(CourseSet(
            name = "Cambridge Plays Animal-O 5s",
            enabled = False,
            courses = [
                Course("Lion", False, [31, 33, 36, 38, 39]),
                Course("Dog", False, [33, 32, 40, 38, 34]),
                Course("Bee", False, [35, 37, 38, 40, 33]),
                Course("Bird", False, [36, 34, 31, 38, 37]),
                Course("Elephant", False, [37, 34, 31, 40, 39]),
                Course("Crab", False, [39, 31, 32, 35, 37]),
            ]
        ))

    def add_course_set(self, course_set: CourseSet):
        # [TODO]: Throw warning if the set of course names is smaller than the set of courses
        # [OR]: represent conflicting courses in the UI somehow
        self.course_sets[course_set.name] = course_set

    def remove_course_set(self, name:str):
        return self.course_sets.pop(name)

    def enable_course_set(self, course_set:str):
        self.set_course_set(course_set, True)

    def disable_course_set(self, course_set:str):
        self.set_course_set(course_set, False)

    def set_course_set(self, course_set, enabled):
        self.course_sets[course_set].enabled = enabled

    def update(self, enabled_dict:dict[str,bool]):
        for k,v in enabled_dict.items():
            self.set_course_set(k, v)

    @property
    def available_course_sets(self) -> list[str]:
        return list(self.course_sets.keys())
    @property
    def enabled_course_sets(self) -> list[str]:
        return [
            course_set.name
            for course_set in self.course_sets.values() if course_set.enabled
        ]

    def get_enabled_courses(self) -> list[Course]:
        return [
            course
            for course_set in self.course_sets.values() if course_set.enabled
            for course in course_set.courses
        ]