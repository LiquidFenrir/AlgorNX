import os
import pygame

data_folder = "AlgorNX"
images_folder = os.path.join(data_folder, "images")
clear_color = (80,80,80)
font_folder = os.path.join(data_folder, "font")
font = pygame.font.Font(os.path.join(font_folder, "font.ttf"), 14)
images = {filename[:-4]: pygame.image.load(os.path.join(images_folder, filename)) for filename in os.listdir(images_folder) if not filename == "robot.gif"}