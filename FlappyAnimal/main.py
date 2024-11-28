#The original image was published by pixeleart on freepik.
#https://www.freepik.com/premium-vector/cute-shark-pixel-art-style_21969559.htm
#I modified and added animation based on the original one.
#Fully respect the artist



import pygame
from pygame.locals import *
import random
import threading
import pyperclip
import csv
import os

from button import Button
from fish import Fish
from bird import Bird
from pipe import Pipe
from character import CharacterImage
from music_player import MusicPlayer 


pygame.init()

#music source setting
api_key = "AIzaSyCLLadKQ6EmuxI0vCUf7GaFU0vXe1QubXI" 
player = MusicPlayer(api_key) 

#constant
screen_width = 864
screen_height = 936
clock = pygame.time.Clock()
fps = 60

#define text font
font_point = pygame.font.SysFont('Bauhaus 93', 60)
font_select = pygame.font.SysFont('Bauhaus 93', 40)
font_screen = pygame.font.SysFont('Bauhaus 93', 125)
font_music = pygame.font.SysFont('Arial', 20)
font_input = pygame.font.SysFont('Arial', 20)

#define colour
white = (255, 255, 255)
black = (0, 0, 0)
red = (212, 68, 68)

#game variable
flying = False
game_over = False
ground_scroll = 0
scroll_speed = 4
pipe_gap = 150 
pipe_frequency = 1700
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Animal')

#load background image
bg = pygame.image.load('FlappyAnimal/img/bg.png')
ground = pygame.image.load('FlappyAnimal/img/ground.png')
#load button image
restart_btn_img = pygame.image.load('FlappyAnimal/img/restart.png')
switch_btn_img = pygame.image.load('FlappyAnimal/img/switch.png')
bird_btn_img = pygame.image.load('FlappyAnimal/img/bird1.png')
fish_btn_img = pygame.image.load('FlappyAnimal/img/fish1.png')
instruction_img = pygame.image.load('FlappyAnimal/img/instruction.png')
#load box image
music_box_img = pygame.image.load('FlappyAnimal/img/music_box.png')
input_box_img = pygame.image.load('FlappyAnimal/img/input_box.png')

#draw text on specific axis
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#draw the instuction when start the game       
def draw_instruction():
    if isinstance(instruction_img, pygame.Surface):
        image_width, image_height = instruction_img.get_size()
        center_x = (screen_width - image_width) // 2
        center_y = (screen_height - image_height) // 2
        
        screen.blit(bg, (0, 0))
        screen.blit(ground, (0, 768))
        screen.blit(instruction_img, (center_x, center_y))

#show the choosing character menu
def show_menu():
    menu_running = True
    selected_character = None
    
    #character selection button with label
    button_bird = CharacterImage(screen_width / 3 - 50, screen_height / 2, bird_btn_img)
    button_fish = CharacterImage(screen_width / 3 + 210, screen_height / 2, fish_btn_img)
    
    while menu_running:
        #draw background
        screen.blit(bg, (0, 0))
        button_bird.draw(screen)
        button_fish.draw(screen)
        screen.blit(ground, (ground_scroll, 768)) 
        
        #show on front screen
        draw_text('FLAPPY ANIMAL', font_screen, red, int(screen_width / 2 - 335), int(screen_height / 2 - 300))
        draw_text('Press', font_select, white, int(screen_width / 3 - 60), int(screen_height / 2 - 80))
        draw_text('(1)', font_select, white, int(screen_width / 3 - 40), int(screen_height / 2 - 45))
        draw_text('Press', font_select, white, int(screen_width / 3 + 210), int(screen_height / 2 - 80))
        draw_text('(2)', font_select, white, int(screen_width / 3 + 230), int(screen_height / 2 - 45))
        
        #define bird & fish button position (maybe unnecessary) !!!
        bird_btn_rect = pygame.Rect(screen_width / 3 - 50, screen_height / 2, 51, 36)
        fish_btn_rect = pygame.Rect(screen_width / 3 + 210, screen_height / 2, 78, 43)   
             
        for event in pygame.event.get():
            #quit the game
            if event.type == pygame.QUIT\
                or event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                
            #choose character
            if event.type == pygame.KEYDOWN:   
                if event.type == pygame.KEYDOWN:
                    if event.key == K_1:  
                        selected_character = "bird"
                        menu_running = False
                    elif event.key == K_2:  
                        selected_character = "fish"
                        menu_running = False

        pygame.display.update()

    return selected_character

#group sprite
pipe_group = pygame.sprite.Group()
character_group = pygame.sprite.Group()

#user's input box
input_x, input_y = 175, 872  
input_width, input_height = 400, 30  
input_box = pygame.Rect(input_x, input_y, input_width, input_height)

#path to the CSV file
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(script_dir, "playlistID.csv")

#log CSV initialization
def initialize_csv():
    if not os.path.exists(csv_file):
        print(f"Creating file at: {os.path.abspath(csv_file)}")  # Debug log
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["No", "Playlist ID"])

#log appending to CSV
def append_to_csv(playlist_id):
    #ensure the CSV file exists
    initialize_csv()
    
    #read the existing data to check for duplicates
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
        
        #extract playlistID column 
        existing_playlist_ids = [row[1] for row in rows[1:]]  
        #check if the input playlist ID already exists (if exist, skip)
        if playlist_id in existing_playlist_ids:
            return  

        #determine the next row number
        next_no = len(rows) if len(rows) > 1 else 1
    
    #add the new data as a new row
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([next_no, playlist_id])
        
initialize_csv()

#user inputs Playlist ID
user_input = ""

#make user input their Youtube Playlist ID
def input_playlist():
    global user_input, playlist_id
    input_active = True
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT\
                or event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  
                    append_to_csv(user_input.strip()) 
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:  
                    user_input = user_input[:-1]
                elif event.key == pygame.K_v and (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
                    user_input += pyperclip.paste() 
                else:
                    user_input += event.unicode  
        
        playlist_id = user_input
                    
        #draw the input prompt
        screen.blit(bg, (0, 0))
        screen.blit(ground, (ground_scroll, 768))
        draw_text('FLAPPY ANIMAL', font_screen, red, int(screen_width / 2 - 335), int(screen_height / 2 - 300))
        screen.blit(input_box_img, (30, 820))
        #draw the input box
        pygame.draw.rect(screen, white, input_box, 0) 
        #render the input text
        text_surface = font_input.render(user_input, True, black)
        screen.blit(text_surface, (input_x, input_y + 5))  

        pygame.display.update()

input_playlist()

#switch character
def switch_character():
    global character  
    selected_character = show_menu()
    character_group.empty()  
    if selected_character == "bird":
        character = Bird(200, int(screen_height / 2))   
    elif selected_character == "fish":
        character = Fish(200, int(screen_height / 2))
        
    character_group.add(character)
    
#restart the game
def restart_game():
    pipe_group.empty()
    character.rect.x = 100
    character.rect.y = int(screen_height / 2)
    character.vel = 0
    character.press = 0
    score = 0
    return score

#define restart button position
restart_btn_rect = pygame.Rect(screen_width // 2 - 50, screen_height // 2 - 125, 120, 42)
restart_btn = Button(screen_width // 2 - 50, screen_height // 2 - 125, restart_btn_img)

#define switch button position
switch_btn_rect = pygame.Rect(screen_width // 2 - 50, screen_height // 2 - 65, 120, 42)
switch_btn = Button(screen_width // 2 - 50, screen_height // 2 - 65, switch_btn_img)

#threading
music_thread = threading.Thread(target = player.run, args = (playlist_id,))
music_thread.daemon = True  
music_thread.start()

#prefetch the video information once and cache it
video_list = player.get_video_info(playlist_id)
video_titles = [video[0] for video in video_list]  
current_index = 0
last_title_update_time = pygame.time.get_ticks()

run = True
show_instruction = True

#sub game loop for showing instruction
while run:    
    #show the instruction
    if show_instruction:
        for event in pygame.event.get():
            if event.type == pygame.QUIT\
                or event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                run = False
            elif event.type == KEYDOWN and event.key == K_p:
                show_instruction = False  
                break

        draw_instruction()
        pygame.display.update()
        continue 
    
    switch_character()

    #main game loop
    while run:
        clock.tick(fps)

        #draw background
        screen.blit(bg, (0, 0))
        character_group.update(flying, game_over)
        character_group.draw(screen)
        pipe_group.draw(screen)
        screen.blit(ground, (ground_scroll, 768))
        
        #draw music box
        screen.blit(music_box_img, (30, 820))
        previous_btn_rect = pygame.Rect(43, 870, 35, 35)
        play_btn_rect = pygame.Rect(88, 870, 35, 35)
        next_btn_rect = pygame.Rect(132, 870, 35, 35)
    
        playlist_id = user_input

        #render realtime title for current song
        current_time = pygame.time.get_ticks()
        if current_time - last_title_update_time:
            current_index = (current_index + 1) % len(video_titles)
            current_title = player.video_list[player.current_index][0]    
            last_title_update_time = current_time
            current_index = (current_index + 1) % len(video_titles)
            music_info = f"Current song: {current_title}"

        draw_text(f'{music_info}', font_music, white, 45, 835)
        
        #check the score
        if len(pipe_group) > 0:
            if character_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
                and character_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
                    pass_pipe = True
            if pass_pipe == True:
                if character_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False
            
        #score        
        if score == 10:
            draw_text('GOOD!', font_point, white, int(screen_width / 2 - 57), int(screen_height / 2 - 300))
        elif score == 20:
            draw_text('IMPRESSIVE!', font_point, white, int(screen_width / 2 - 120), int(screen_height / 2 - 300))
        elif score == 30:
            draw_text('REALLY!?!?', font_point, white, int(screen_width / 2 - 95), int(screen_height / 2 - 300))
        elif score == 40:
            draw_text('BRO IS COOKING!', font_point, white, int(screen_width / 2 - 160), int(screen_height / 2 - 300))
        elif score == 50:
            draw_text('WINNER WINNER CHICKEN DINNER!', font_point, white, int(screen_width / 2 - 360), int(screen_height / 2 - 300))
        
        draw_text(str(score), font_point, white, int(screen_width / 2), 30)

        #check the collision with pipe
        if pygame.sprite.groupcollide(character_group, pipe_group, False, False)\
            or character.rect.top < 0:
            game_over = True

        #check if character hit the ground
        if character.rect.bottom >= 768:
            game_over = True
            flying = False

        #generate new pipe
        if game_over == False and flying == True:
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
                pipe_group.add(btm_pipe)
                top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
                pipe_group.add(top_pipe)
                last_pipe = time_now    
            
            #draw and scroll the ground
            ground_scroll -= scroll_speed
            if abs(ground_scroll) > 35:
                ground_scroll = 0
            pipe_group.update()   
            
        #draw restart & switch button when game is over
        if game_over == True:
                restart_btn.draw(screen)
                switch_btn.draw(screen)
                    
        for event in pygame.event.get():
            #quit the game
            if event.type == pygame.QUIT\
                or event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                run = False
                
            #restart game & switch character
            if (event.type == pygame.KEYDOWN and game_over == True)\
                or (event.type == pygame.MOUSEBUTTONDOWN and game_over == True):
                #click the mouse to choose
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos  
                    if restart_btn_rect.collidepoint(mouse_pos):
                        game_over = False 
                        score = restart_game()
                    elif switch_btn_rect.collidepoint(mouse_pos):
                        switch_character()
                        game_over = False 
                        score = restart_game()
                #press the key to choose
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_r:
                        game_over = False 
                        score = restart_game()
                    elif event.key == K_c:
                        switch_character()
                        game_over = False 
                        score = restart_game()
                            
            #gameplay
            if event.type == pygame.KEYDOWN\
                and flying == False and game_over == False:
                if event.key == K_SPACE:
                    flying = True

            #control music box
            get_stream_url = MusicPlayer(api_key)
            playing_song = True   
            if (event.type == pygame.KEYDOWN and game_over == True)\
                or (event.type == pygame.MOUSEBUTTONDOWN and game_over == True):
                #click the mouse to choose
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos  
                    if play_btn_rect.collidepoint(mouse_pos):
                        player.pause()
                        playing_song = not playing_song
                    elif next_btn_rect.collidepoint(mouse_pos):
                        player.next_song()
                    elif previous_btn_rect.collidepoint(mouse_pos):
                        player.previous_song()
                #press the key to choose
                elif event.type == pygame.KEYDOWN:
                    #play/pause song
                    if event.key == K_k:
                        player.pause()
                        playing_song = not playing_song
                    #next song
                    elif event.key == K_l:
                        player.next_song()
                    #back song
                    elif event.key == K_j:
                        player.previous_song()
        
        #exit the inner game loop if quitting the game
        if not run:
            break
        
        pygame.display.update() 

pygame.quit()
