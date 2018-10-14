import os, sys
from json import load
import pygame
import grid_info

pygame.init()

import AlgorNX_runner as runner
import AlgorNX_editor as editor
import AlgorNX_images as images

def draw_test_on_surface(surface, test, robot_position, robot_direction):
    for y, line in enumerate(test, 1):
        for x, square_type in enumerate(line, 1):
            surface.blit(images.images[grid_info.get_image_from_type(square_type)], (x*grid_info.IMAGE_SIZE, y*grid_info.IMAGE_SIZE))

        surface.blit(images.images["robot_{}".format(robot_direction)], (robot_position["x"]*grid_info.IMAGE_SIZE, robot_position["y"]*grid_info.IMAGE_SIZE))

def load_level(level_folder):
    with open(os.path.join(level_folder, "level.json")) as f:
        level_data = load(f)
    return level_data

def load_program(level_folder):
    try:
        with open(os.path.join(level_folder, "program.py")) as f:
            program_data = f.read()
        return program_data
    except OSError:
        return None

def save_program(level_folder, source):
    with open(os.path.join(level_folder, "program.py"), "w") as f:
        f.write(source)

class AlgorNX():
    def add_button_text(self, key, value):
        self.running_buttons_text[key] = (images.font.render(value, False, self.text_color), images.font.size(value))

    def __init__(self, level_folder):
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720), pygame.HWSURFACE)
        self.screen_surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.program_runner = None

        self.control_buttons_height = 40
        self.tests_width = 480
        self.control_buttons_surface = self.screen_surface.subsurface((0, 0, self.tests_width, self.control_buttons_height))

        self.level_data = load_level(level_folder)
        self.program_source = load_program(level_folder)

        self.text_color = (0,0,0)

        self.test_header_height = 24
        self.actual_tests_width = (self.level_data["size"]["width"] + 1) * grid_info.IMAGE_SIZE
        self.actual_tests_height = (self.level_data["size"]["height"] + 1) * grid_info.IMAGE_SIZE

        self.header_rect_outer = pygame.Surface((self.tests_width-10, self.test_header_height))
        self.header_rect_outer.fill((161, 207, 237))
        self.header_rect_outer = (self.header_rect_outer, (0, 0))
        self.header_rect_inner = pygame.Surface((self.tests_width-10-4, self.test_header_height-4))
        self.header_rect_inner.fill((221, 237, 248))
        self.header_rect_inner = (self.header_rect_inner, (2, 2))

        self.tests_header_text = [(images.font.render("Test {}".format(i+1), False, self.text_color), (4,4)) for i in range(len(self.level_data["tests"]))]
        self.tests_header_arrow_right = (images.font.render("\u25ba", False, self.text_color), (self.tests_width-26,2))
        self.tests_header_arrow_down = (images.font.render("\u25bc", False, self.text_color), (self.tests_width-26,2))

        self.test_coords_text = [(images.font.render(str(i+1), False, self.text_color), images.font.size(str(i+1))[0]) for i in range(max(self.level_data["size"]["width"], self.level_data["size"]["height"]))]

        self.tests_surface = pygame.Surface((self.actual_tests_width, self.actual_tests_height))

        self.tests_surface.fill(images.clear_color)
        for x in range(self.level_data["size"]["width"]):
            self.tests_surface.blit(self.test_coords_text[x][0], ((x+1)*grid_info.IMAGE_SIZE + (grid_info.IMAGE_SIZE - self.test_coords_text[x][1])//2, 3))

        for y in range(self.level_data["size"]["height"]):
            self.tests_surface.blit(self.test_coords_text[y][0], ((grid_info.IMAGE_SIZE - self.test_coords_text[y][1])//2, (y+1)*grid_info.IMAGE_SIZE + 2))

        self.running_button_width, self.running_button_height = 80, 32
        self.running_button_gap = 15
        self.running_button_outer = pygame.Surface((self.running_button_width, self.running_button_height))
        self.running_button_outer.fill((161, 207, 237))
        self.running_button_inner = pygame.Surface((self.running_button_width-4, self.running_button_height-4))
        self.running_button_inner.fill((221, 237, 248))

        self.test_running = False
        self.running_buttons_text = {}
        self.add_button_text("validate", "Validate")
        self.add_button_text("to_run", "Run")
        self.add_button_text("running", "Stop")
        self.add_button_text("normal_speed", ">")
        self.add_button_text("fast_speed", ">>")
        self.add_button_text("instant_speed", ">>>")

        self.running_buttons_handlers = (
            self.validate_program_button_action,
            self.run_program_button_action,
            lambda: self.select_speed_mode(0),
            lambda: self.select_speed_mode(1),
            lambda: self.select_speed_mode(2),
        )

        green_color = (0,255,128)
        self.red_color = (255,60,60)
        self.success_text = images.font.render("Test passed sucessfully!", False, green_color)
        self.validate_success_text = images.font.render("All tests passed sucessfully!", False, green_color)
        self.failure_text = images.font.render("Test failed!", False, self.red_color)

        self.editor_surface_width = 1280-self.tests_width
        self.editor_surface_height = 720-self.control_buttons_height
        self.editor_surface = self.screen_surface.subsurface((self.tests_width, 0, self.editor_surface_width, self.editor_surface_height))
        self.message_surface = pygame.Surface((1280-self.tests_width, self.control_buttons_height))
        self.message_surface.fill(images.clear_color)

        self.editor = editor.Editor(self.editor_surface, self.program_source, self.level_data["allowed_keywords"])

        self.select_test(0)

    def mainloop(self):
        while self.running:
            self.draw()
            self.events()

            self.clock.tick(60)

    def clear_message(self):
        self.message_surface.fill(images.clear_color)

    def set_message_on_surface(self, surface):
        self.clear_message()
        self.message_surface.blit(surface, ((self.message_surface.get_width() - surface.get_width())//2, (self.message_surface.get_height() - surface.get_height())//2))

    def set_error_message(self, message):
        self.set_message_on_surface(images.font.render(message, False, self.red_color))

    def draw_source_running(self, lineno):
        pass

    def draw_control_buttons(self):
        control_buttons_surfaces = []

        x_speed = x_text = 6

        control_buttons_surfaces.append((self.running_button_outer, (x_speed+4, 4)))
        x_speed += self.running_button_width + self.running_button_gap
        control_buttons_surfaces.append((self.running_button_outer, (x_speed+4, 4)))
        x_speed += self.running_button_width + self.running_button_gap
        control_buttons_surfaces.append((self.running_button_outer, (x_speed+4, 4)))
        x_speed += self.running_button_width + self.running_button_gap
        control_buttons_surfaces.append((self.running_button_outer, (x_speed+4, 4)))
        x_speed += self.running_button_width + self.running_button_gap
        control_buttons_surfaces.append((self.running_button_outer, (x_speed+4, 4)))
        x_speed += self.running_button_width + self.running_button_gap

        def add_button_text_to_surfaces(self, id):
            nonlocal control_buttons_surfaces
            nonlocal x_text

            x = x_text + (self.running_button_width - self.running_buttons_text[id][1][0])//2
            y = 6 + (self.running_button_height - self.running_buttons_text[id][1][1])//2
            control_buttons_surfaces.append((self.running_buttons_text[id][0], (x, y)))
            x_text += self.running_button_width + self.running_button_gap

        add_button_text_to_surfaces(self, "validate")

        if self.test_running:
            control_buttons_surfaces.append((self.running_button_inner, (x_text+6, 6)))
            add_button_text_to_surfaces(self, "running")

            control_buttons_surfaces.append((self.running_button_inner, (x_text+6 + (self.running_button_width + self.running_button_gap)*self.selected_speed, 6)))
        else:
            add_button_text_to_surfaces(self, "to_run")

        add_button_text_to_surfaces(self, "normal_speed")
        add_button_text_to_surfaces(self, "fast_speed")
        add_button_text_to_surfaces(self, "instant_speed")

        self.control_buttons_surface.blits(control_buttons_surfaces, False)

    def draw_tests_headers(self):
        for i, test_header in enumerate(self.tests_header_surfaces):
            surfaces = [self.header_rect_outer]
            if i == self.selected_test:
                surfaces.append(self.header_rect_inner)
                surfaces.append(self.tests_header_arrow_down)
            else:
                surfaces.append(self.tests_header_arrow_right)

            surfaces.append(self.tests_header_text[i])

            test_header.blits(surfaces, False)

    def draw(self):
        self.screen.fill(images.clear_color)

        self.editor.draw()

        self.draw_control_buttons()
        self.draw_tests_headers()

        if self.test_running:
            self.framecnt += 1
            self.framecnt %= 240
            try:
                speeds = [1, 20, 60]
                if self.framecnt % speeds[2-self.selected_speed] == 0:
                    self.program_runner.update()
                    self.draw_source_running(self.program_runner.line_no)
                self.program_runner.draw(draw_test_on_surface, self.tests_surface)
            except Exception as e:
                self.set_error_message(str(e))
                self.run_program_button_action()  # Stop the test

        if self.test_running and self.program_runner.program_done:
            if self.program_runner.is_success():
                self.set_message_on_surface(self.success_text)
            else:
                self.set_message_on_surface(self.failure_text)
            self.run_program_button_action()  # Stop the test

        self.screen_surface.blit(self.message_surface, (1280-self.message_surface.get_width(), 720-self.message_surface.get_height()))

        self.screen_surface.blit(self.tests_surface, self.tests_surface_pos)
        pygame.display.update()

    def validate_program_button_action(self):
        if not self.test_running:
            self.validating = True

    def run_program_button_action(self):
        if self.test_running:
            self.test_running = False
            self.program_runner.stop()
            self.program_runner = None
        else:
            try:
                self.program_runner = runner.validate_and_start_program(self.program_source, self.level_data, self.selected_test)
                self.test_running = True
                self.selected_speed = 0
                self.framecnt = 0
                self.clear_message()
            except Exception as e:
                self.set_error_message(str(e))

    def select_speed_mode(self, speed_mode):
        if self.test_running:
            self.selected_speed = speed_mode

    def events(self):
        events = pygame.event.get()
        pos = pygame.mouse.get_pos()
        self.editor.handle_mouse_hover(pos)
        for e in events:
            if e.type == pygame.QUIT:
                if self.program_runner:
                    self.program_runner.stop()
                    self.program_runner = None
                self.running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if not self.test_running:
                        for i, test_header in enumerate(self.tests_header_rects):
                            if test_header.collidepoint(pos):
                                self.select_test(i)
                                break

                    for i, handler in enumerate(self.running_buttons_handlers):
                        if pygame.Rect(self.running_button_gap*(i+1) + self.running_button_width*i, 4, self.running_button_width, self.running_button_height).collidepoint(pos):
                            handler()
                            break

                    self.editor.handle_mouse_click(pos)

    def select_test(self, id):
        self.selected_test = id
        total_extra_height = 0
        self.tests_header_rects = []
        self.tests_header_surfaces = []
        for i in range(len(self.level_data["tests"])):
            y = self.control_buttons_height + total_extra_height
            self.tests_header_rects.append(pygame.Rect(5, y, self.tests_width-10, self.test_header_height))
            self.tests_header_surfaces.append(self.screen_surface.subsurface(self.tests_header_rects[-1]))
            y += self.test_header_height + 4
            total_extra_height += self.test_header_height + 4
            if i == self.selected_test:
                self.tests_surface_pos = (20, y)
                total_extra_height += self.actual_tests_height + 4

        draw_test_on_surface(self.tests_surface, self.level_data["tests"][self.selected_test]["shown"], self.level_data["spawn"], "right")

def main():
    game = AlgorNX(sys.argv[1])
    game.mainloop()

if __name__ == "__main__":
    main()
