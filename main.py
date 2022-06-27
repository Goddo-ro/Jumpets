# Arts by pzUH https://www.freepik.com/pzuh
# Give Me A Smile by Free Music | https://soundcloud.com/fm_freemusic
# Music promoted by http://chosic.com/
# Creative Commons Attribution 3.0 Unported License
# https://creativecommons.org/licenses/by/3.0/deed.en_US
# Background music of game by CodeManu https://opengameart.org/users/codemanu
# Game over music by mixkit https://mixkit.co/free-sound-effects/game-over/


import pygame
import random
import pygame_gui
from settings import *
from sprites import *
from os import path


class Game:
    def __init__(self):
        # initialize game window, etc
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.load_data()
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font(FONT_NAME)
        self.skin_folder = "cat"
        self.playing = False

    def load_data(self):
        self.direction = path.dirname(__file__)
        with open(path.join(self.direction, HS_FILE), 'r') as file:
            try:
                self.highscore = int(file.read())
            except:
                self.highscore = 0
        self.sound_direction = path.join(self.direction, "data", "sound")
        self.jump_sound = pygame.mixer.Sound(path.join(self.sound_direction, "jump.wav"))
        self.powerup_sound = pygame.mixer.Sound(path.join(self.sound_direction, "powerup.wav"))
        self.clouds_images = [load_image("clouds", "Cloud {}.png".format(i)) for i in range(1, 9)]

    def new(self):
        # start a new game
        self.score = 0
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)
        for plat in PLATFORM_LIST:
            platform = Platform(self, *plat)
            self.all_sprites.add(platform)
            self.platforms.add(platform)
        self.mob_timer = 0
        pygame.mixer.music.load(path.join(self.sound_direction, BACKGROUND_MUSIC))
        pygame.mixer.music.set_volume(0.2)
        self.run()

    def run(self):
        pygame.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pygame.mixer.music.fadeout(500)

    def update(self):
        self.all_sprites.update()

        now = pygame.time.get_ticks()
        if now - self.mob_timer > ENEMIES_SPAWN_TIME + choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Enemy(self)

        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, pygame.sprite.collide_mask)
        if enemy_hits:
            self.playing = False

        if self.player.velocity.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = max(hits, key=lambda x: x.rect.bottom)
                if self.player.pos.x < lowest.rect.right - 7 and self.player.pos.x > lowest.rect.left + 7 and\
                        self.player.pos.y < lowest.rect.bottom:
                    self.player.pos.y = lowest.rect.top
                    self.player.velocity.y = 0
                    self.player.jumping = False
                    self.player.double_jump = False

        for accelerator in pygame.sprite.spritecollide(self.player, self.powerups, True):
            if accelerator.type == "boost":
                self.powerup_sound.play()
                self.player.velocity.y = -BOOST_POWER
                self.player.jumping = False
                self.player.double_jump = False
                self.player.powering = True

        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.velocity.y), 2)
            if randrange(100) < 4:
                Cloud(self)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.velocity.y // 2), 2)
            for enemy in self.enemies:
                enemy.rect.y += max(abs(self.player.velocity.y), 2)
            for platform in self.platforms:
                platform.rect.y += max(abs(self.player.velocity.y), 2)
                if platform.rect.top >= HEIGHT:
                    platform.kill()
                    self.score += 10

        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.velocity.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()

        if len(self.platforms) == 0:
            self.playing = False

        if self.player.rect.bottom < HEIGHT:
            while len(self.platforms) < 6:
                width = 100
                platform = Platform(self, random.randrange(0, WIDTH - width),
                                    random.randrange(-75, -30))
                if not pygame.sprite.spritecollide(platform, self.platforms, True):
                    self.platforms.add(platform)
                    self.all_sprites.add(platform)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.pause()
                    self.show_menu_screen()
                    pygame.mixer.music.unpause()
                if event.key == pygame.K_SPACE:
                    self.player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        pygame.display.flip()

    def show_go_screen(self):
        if not self.running:
            return
        pygame.mixer.Sound(path.join(self.sound_direction, GAME_OVER_MUSIC)).play()
        pygame.mixer.music.set_volume(0.2)
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Score: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.direction, HS_FILE), 'w') as file:
                file.write(str(self.score))
        else:
            self.draw_text("High Score: " + str(self.highscore), 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pygame.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False
        pygame.mixer.stop()

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def show_menu_screen(self):
        pygame.init()

        skins = [pygame.transform.scale(load_image("cat", "standing", "Idle 1.png"), (45, 55)),
                 pygame.transform.scale(load_image("dog", "standing", "Idle 1.png"), (45, 55))]
        folders = ["cat", "dog"]
        id = 0
        fon = pygame.image.load('fon.jpg')

        pygame.display.set_caption('Menu')
        surface = pygame.display.set_mode((WIDTH, HEIGHT))

        back = pygame.Surface((WIDTH, HEIGHT))
        back.blit(fon, (-60, -70))
        back.blit(skins[id], (330, 240))

        manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        start = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 150), (100, 50)),
            text='Start',
            manager=manager
        )
        exit = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 350), (100, 50)),
            text='Exit',
            manager=manager
        )
        right_arrow = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((390, 260), (35, 35)),
            text='>',
            manager=manager
         )
        left_arrow = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((275, 260), (35, 35)),
            text='<',
            manager=manager
        )


        def show_confirmation_dialog():
            confirmation_dialog = pygame_gui.windows.UIConfirmationDialog(
                rect=pygame.Rect((100, 150), (300, 200)),
                manager=manager,
                window_title='Confirmation',
                action_long_desc='Are you sure you want to get out of this beautiful game?',
                action_short_name='OK',
                blocking=True
            )


        running = True
        while running:
            time_delta = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    show_confirmation_dialog()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.playing:
                        running = False
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                        running = False
                        self.running = False
                        self.playing = False
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if event.ui_element == start:
                            running = False
                            self.skin_folder = folders[id]
                            self.new()
                        if event.ui_element == right_arrow:
                            back.blit(fon, (-60, -70))
                            id = (id + 1) % 2
                            back.blit(skins[id], (330, 240))
                        if event.ui_element == left_arrow:
                            back.blit(fon, (-60, -70))
                            id = (id - 1) % -2
                            back.blit(skins[id], (330, 240))
                        if event.ui_element == exit:
                            show_confirmation_dialog()
                manager.process_events(event)
            manager.update(time_delta)
            surface.blit(back, (0, 0))
            manager.draw_ui(surface)
            pygame.display.update()


game = Game()
game.show_menu_screen()
while game.running:
    game.new()
    game.show_go_screen()

pygame.quit()
