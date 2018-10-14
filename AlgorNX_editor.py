import pygame
from collections import OrderedDict
import AlgorNX_images as images

EDITOR_BUTTONS_SIZE = 40
BLOCK_HEIGHT = 32

class EditorMenu():
    def __init__(self, image_id: str, color, sub_menus):
        self.image = images.images[image_id]
        sub_menus_surfaces = (pygame.Surface((108, EDITOR_BUTTONS_SIZE//2)) for i in range(len(sub_menus)))
        self.sub_menus = []
        for sub_menu_surface, sub_menu_text in zip(sub_menus_surfaces, sub_menus):
            text = images.font.render(sub_menu_text, False, (255,255,255))
            sub_menu_surface.fill(color)
            sub_menu_surface.blit(text, ((sub_menu_surface.get_width() - text.get_width())//2, (sub_menu_surface.get_height() - text.get_height())//2))
            self.sub_menus.append(sub_menu_surface)

class Editor():
    def __init__(self, surface, program_source, allowed_keywords):
        self.editor_width = surface.get_width()
        self.editor_buttons_size = 40
        self.surface = surface

        self.scroll_y = self.scroll_x = 0
        self.selected_menu = -1
        self.source = []

        assignment_sub_menus = (
            "Assign",
            "Add assign",
            "Sub assign",
            "Mul assign",
            "Div assign",
            "Idiv assign",
            "Mod assign",
            "Exp assign",
            "Exp assign",

            "Lsh assign",
            "Rsh assign",
            "And assign",
            "Or assign",
            "Xor assign",
        )

        punctuation_sub_menus = ["Open paren", "Closed paren"]
        if allowed_keywords["["]:
            punctuation_sub_menus.append("Open bracket")
            punctuation_sub_menus.append("Closed bracket")
        if allowed_keywords["{"]:
            punctuation_sub_menus.append("Open brace")
            punctuation_sub_menus.append("Closed brace")
        punctuation_sub_menus.append("Comma")

        flow_control_sub_menus = []
        if allowed_keywords["if"]:
            flow_control_sub_menus.append("if")

        if allowed_keywords["else"]:
            flow_control_sub_menus.append("elif")
            flow_control_sub_menus.append("else")

        if allowed_keywords["while"]:
            flow_control_sub_menus.append("While loop")
        if allowed_keywords["for"]:
            flow_control_sub_menus.append("For loop")

        if allowed_keywords["continue"]:
            flow_control_sub_menus.append("Continue loop")
        if allowed_keywords["break"]:
            flow_control_sub_menus.append("Break out of loop")

        if allowed_keywords["def"]:
            flow_control_sub_menus.append("New function")

        operators_sub_menus =  [
            "Add",
            "Subtract",
            "Multiply",
            "Divide",
            "Integer divide",
            "Modulus",
            "Exponent",

            "Left shift",
            "Right shift",
            "Bitwise and",
            "Bitwise or",
            "Bitwise not",
            "Xor",

            "Less than",
            "Less equal",
            "Greater than",
            "Greater equal",

            "Equal",
            "Not equal",
        ]

        if allowed_keywords["and"]:
            operators_sub_menus.append("Logical and")
        if allowed_keywords["or"]:
            operators_sub_menus.append("Logical or")
        if allowed_keywords["not"]:
            operators_sub_menus.append("Logical not")

        self.editor_buttons = [
            EditorMenu("variables", (238, 125, 22), ("Variable", "Function call")),
            EditorMenu("assignment", (44, 165, 226), assignment_sub_menus),
            EditorMenu("punctuation", (138, 85, 215), punctuation_sub_menus),
            EditorMenu("operators", (92, 183, 18), operators_sub_menus),
        ]
        if flow_control_sub_menus:
            self.editor_buttons.append(EditorMenu("flow_control", (225, 169, 26), flow_control_sub_menus))

        self.buttons_with_pos = [(button.image, ((112 + EDITOR_BUTTONS_SIZE)*i, 0)) for i, button in enumerate(self.editor_buttons)]
        self.sub_menus_with_pos = []
        for x, menu in enumerate(self.editor_buttons):
            self.sub_menus_with_pos.append([])
            for y, sub_menu in enumerate(menu.sub_menus):
                self.sub_menus_with_pos[-1].append((sub_menu, (self.buttons_with_pos[x][1][0] + EDITOR_BUTTONS_SIZE + 2, y*EDITOR_BUTTONS_SIZE//2 + (y+1)*2)))

        self.block_in_hand = None

    def draw(self):
        start = self.scroll_y // BLOCK_HEIGHT
        y = self.scroll_y

        self.surface.blits(self.buttons_with_pos, False)
        if self.selected_menu >= 0:
            self.surface.blits(self.sub_menus_with_pos[self.selected_menu], False)

    def handle_mouse_click(self, pos):
        off = self.surface.get_offset()[0]
        found = False
        for i, tup in enumerate(self.buttons_with_pos):
            if pygame.Rect((off + tup[1][0], tup[1][1]), (EDITOR_BUTTONS_SIZE, EDITOR_BUTTONS_SIZE)).collidepoint(pos):
                self.selected_menu = i
                found = True
                break

        if not found:
            self.selected_menu = -1

    def handle_mouse_hover(self, pos):
        if self.block_in_hand:
            self.pos = pos
        else:
            self.pos = None

    def get_source(self):
        return "\n".join(" ".join(repr(block) for block in line) for line in self.source)

