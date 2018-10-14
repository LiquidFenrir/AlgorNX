import sys
from copy import deepcopy
import ast
import bdb
import threading
import grid_info

class ProgramValidator(ast.NodeVisitor):
    def visit_Import(self, node):
        raise Exception("Not allowed to import, for safety")

    def visit_ImportFrom(self, node):
        raise Exception("Not allowed to import, for safety")

    def visit_Not(self, node):
        if not self.allowed_not:
            raise Exception("Disabled keywords: not")

    def visit_Or(self, node):
        if not self.allowed_or:
            raise Exception("Disabled keywords: or")

    def visit_And(self, node):
        if not self.allowed_and:
            raise Exception("Disabled keywords: and")

    def visit_If(self, node):
        if not self.allowed_if:
            raise Exception("Disabled keywords: if")

    def visit_For(self, node):
        if not self.allowed_for:
            raise Exception("Disabled keywords: for")

    def visit_While(self, node):
        if not self.allowed_while:
            raise Exception("Disabled keywords: while")

    def visit_Continue(self, node):
        if not self.allowed_continue:
            raise Exception("Disabled keywords: continue")

    def visit_Break(self, node):
        if not self.allowed_break:
            raise Exception("Disabled keywords: break")

    def visit_FunctionDef(self, node):
        if not self.allowed_def:
            raise Exception("Disabled keywords: def")

    def visit_Subscript(self, node):
        if not self.allowed_bracket:
            raise Exception("Disabled keywords: brackets [ ]")

    def visit_Index(self, node):
        if not self.allowed_bracket:
            raise Exception("Disabled keywords: brackets [ ]")

    def visit_List(self, node):
        if not self.allowed_bracket:
            raise Exception("Disabled keywords: brackets [ ]")

    def visit_Dict(self, node):
        if not self.allowed_brace:
            raise Exception("Disabled keywords: braces { }")

    def visit_Set(self, node):
        if not self.allowed_brace:
            raise Exception("Disabled keywords: braces { }")

    def visit_Name(self, node):
        if node.id in self.disabled_functions:
            raise Exception("Disabled function: " + node.id)

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def validate(self, source, allowed_keywords):
        self.allowed_for = allowed_keywords["for"]
        self.allowed_while = allowed_keywords["while"]
        self.allowed_if = allowed_keywords["if"]
        self.allowed_else = allowed_keywords["else"]
        self.allowed_break = allowed_keywords["break"]
        self.allowed_continue = allowed_keywords["continue"]
        self.allowed_not = allowed_keywords["not"]
        self.allowed_and = allowed_keywords["and"]
        self.allowed_or = allowed_keywords["or"]
        self.allowed_def = allowed_keywords["def"]
        self.allowed_list = allowed_keywords["list"]
        self.allowed_dict = allowed_keywords["dict"]
        self.allowed_set = allowed_keywords["set"]
        self.allowed_bracket = allowed_keywords["["]
        self.allowed_brace = allowed_keywords["{"]

        self.disabled_functions = {"exec", "eval", "input", "print"}
        if not self.allowed_list:
            self.disabled_functions.add("list")
        if not self.allowed_dict:
            self.disabled_functions.add("dict")
        if not self.allowed_set:
            self.disabled_functions.add("set")

        self.visit(source)

class ActualRunner(bdb.Bdb):
    def __init__(self):
        bdb.Bdb.__init__(self)
        self.line_no = -1

    # Override Bdb methods
    def user_call(self, frame, argument_list):
        """Called if we might stop in a function."""
        if frame.f_code.co_filename == "<string>":
            self.set_step()
        else:
            self.set_return(frame)

    def user_line(self, frame):
        """Called when we stop or break at a line."""
        self.line_end_event.set()
        self.run_line_event.wait()
        self.run_line_event.clear()
        if self.stop_thread:
            raise bdb.BdbQuit
        else:
            self.set_step()
            self.line_no = frame.f_lineno

    def user_return(self, frame, return_value):
        """Called when a return trap is set here."""
        name = frame.f_code.co_name or "<unknown>"
        if name == "<module>":
            self.program_done = True
            raise bdb.BdbQuit
        self.set_step() # continue

    def user_exception(self, frame, exc_info):
        """Called when we stop on an exception."""
        raise exc_info[1]

class ProgramRunner(ActualRunner):
    def get_square_under_robot(self):
        return self.grid[self.robot_position["y"]-1][self.robot_position["x"]-1]

    def set_square_under_robot(self, new_type):
        self.grid[self.robot_position["y"]-1][self.robot_position["x"]-1] = new_type

    def robot_go_up(self):
        if self.robot_position["y"] > 1:
            self.robot_position["y"] -= 1
            self.robot_direction = "up"
        else:
            raise Exception("Moving out of the grid!")

    def robot_go_down(self):
        if self.robot_position["y"] < self.level_size["height"]:
            self.robot_position["y"] += 1
            self.robot_direction = "down"
        else:
            raise Exception("Moving out of the grid!")

    def robot_go_left(self):
        if self.robot_position["x"] > 1:
            self.robot_position["x"] -= 1
            self.robot_direction = "left"
        else:
            raise Exception("Moving out of the grid!")

    def robot_go_right(self):
        if self.robot_position["x"] < self.level_size["width"]:
            self.robot_position["x"] += 1
            self.robot_direction = "right"
        else:
            raise Exception("Moving out of the grid!")

    def robot_column(self):
        return self.robot_position["x"]

    def robot_line(self):
        return self.robot_position["y"]

    def robot_on_painted(self):
        return self.get_square_under_robot() == grid_info.PAINTED

    def robot_paint(self):
        square = self.get_square_under_robot()
        if square == grid_info.MARKER:
            self.set_square_under_robot(grid_info.PAINTED)
        else:
            raise Exception("Attempt to paint an unmarked square")

    def robot_grab(self):
        if self.robot_holding == "":
            if self.on_item():
                self.robot_holding = reversed_names[self.get_square_under_robot()]
                self.set_square_under_robot(grid_info.EMPTY)
            else:
                raise Exception("No item to grab!")
        else:
            raise Exception("Already holding an item!")

    def robot_release(self):
        square = self.get_square_under_robot()
        if square == grid_info.EMPTY:
            self.set_square_under_robot(square | grid_info.FILLED)
            self.robot_holding = ""
        elif square & grid_info.HOLE:
            if square & grid_info.FILLED:
                raise Exception("Hole is already filled!")
            else:
                if (square & ~grid_info.HOLE) == (self.holding_to_type[self.robot_holding] & ~grid_info.FILLED):
                    self.set_square_under_robot(square | grid_info.FILLED)
                    self.robot_holding = ""
                else:
                    raise Exception("The shape held doesn't match the shape of the hole!")
        else:
            raise Exception("Can't release item here!")

    def robot_read_number(self):
        square = self.get_square_under_robot()
        if square & grid_info.NUMBER:
            return grid_info.square_number_get(square)
        else:
            raise Exception("No number to read!")

    def robot_write_number(self, number):
        square = self.get_square_under_robot()
        if square & grid_info.NUMBER or square == grid_info.EMPTY:
            self.set_square_under_robot(grid_info.square_number_set(number))
        else:
            raise Exception("Can't write a number here!")

    def robot_on_item(self):
        return bool(self.get_square_under_robot() & grid_info.CIRCLE)  # Circle contains both bits about shapes

    def robot_on_hole(self):
        return bool(self.get_square_under_robot() & grid_info.HOLE)

    def robot_on_triangle(self):
        return self.get_square_under_robot() & grid_info.CIRCLE == grid_info.TRIANGLE

    def robot_on_square(self):
        return self.get_square_under_robot() & grid_info.CIRCLE == grid_info.SQUARE

    def robot_on_circle(self):
        return self.get_square_under_robot() & grid_info.CIRCLE == grid_info.CIRCLE

    def robot_on_filled_shape(self):
        return self.robot_on_item() and self.get_square_under_robot() & grid_info.FILLED

    def robot_on_dotted_shape(self):
        return self.robot_on_item() and not self.get_square_under_robot() & grid_info.FILLED

    def __init__(self, level_data, test_id, source):
        self.level_size = level_data["size"]
        self.robot_position = deepcopy(level_data["spawn"])
        self.grid = deepcopy(level_data["tests"][test_id]["shown"])
        self.wanted_result = deepcopy(level_data["tests"][test_id]["wanted"])
        self.robot_direction = "right"
        self.robot_holding = ""
        self.source = source
        self.program_done = False
        self.exc_info = None

        self.holding_to_type = {
            "grid_triangle_dotted": grid_info.SHAPE_TRIANGLE,
            "grid_triangle_filled": grid_info.SHAPE_TRIANGLE | grid_info.FILLED,

            "grid_square_dotted": grid_info.SHAPE_SQUARE,
            "grid_square_filled": grid_info.SHAPE_SQUARE | grid_info.FILLED,

            "grid_circle_dotted": grid_info.SHAPE_CIRCLE,
            "grid_circle_filled": grid_info.SHAPE_CIRCLE | grid_info.FILLED,
        }
        robot_functions = {
            "up": self.robot_go_up,
            "down": self.robot_go_down,
            "left": self.robot_go_left,
            "right": self.robot_go_right,

            "column": self.robot_column,
            "line": self.robot_line,

            "on_painted": self.robot_on_painted,
            "paint": self.robot_paint,

            "grab": self.robot_grab,
            "release": self.robot_release,

            "read_number": self.robot_read_number,
            "write_number": self.robot_write_number,

            "on_item": self.robot_on_item,
            "on_hole": self.robot_on_hole,

            "on_triangle": self.robot_on_triangle,
            "on_square": self.robot_on_square,
            "on_circle": self.robot_on_circle,

            "on_filled_shape": self.robot_on_filled_shape,
            "on_dotted_shape": self.robot_on_dotted_shape,
        }
        self.actual_functions = {k: v for k, v in robot_functions.items() if level_data["allowed_functions"][k]}
        
        ActualRunner.__init__(self)

        self.stop_thread = False
        self.run_line_event = threading.Event()
        self.line_end_event = threading.Event()
        self.run_thread = threading.Thread(target=self.thread_target)
        self.run_thread.start()

    def draw(self, function, surface):
        function(surface, self.grid, self.robot_position, self.robot_direction)

    def is_success(self):
        out = False
        if self.get_square_under_robot() == grid_info.WINNING_SQUARE:
            out = True
        elif self.grid == self.wanted_result:
            out = True

        return out

    def thread_target(self):
        try:
            self.run(self.source, self.actual_functions)
        except Exception as e:
            self.exc_info = sys.exc_info()
        finally:
            self.line_end_event.set()

    def update(self):
        self.line_end_event.clear()
        self.run_line_event.set()
        self.line_end_event.wait()
        self.line_end_event.clear()
        if self.exc_info:
            raise self.exc_info[1].with_traceback(self.exc_info[2])

    def stop(self):
        self.stop_thread = True
        self.run_line_event.set()
        self.run_thread.join()

def validate_and_start_program(program_source, level_data, selected_test):
    source = ast.parse(program_source, filename='program.py', mode='exec')
    ProgramValidator().validate(source, level_data["allowed_keywords"])
    return ProgramRunner(level_data, selected_test, program_source)
