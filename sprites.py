import pygame
import os
from settings import *
from random import randrange, choice
vector = pygame.math.Vector2


def load_image(*name):
    fullname = os.path.join('data', 'images', *name)
    image = pygame.image.load(fullname)
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.walking = False
        self.jumping = False
        self.powering = False
        self.double_jump = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.standing_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.pos = vector(WIDTH / 2, HEIGHT / 2)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0, 0)

    def load_images(self):
        self.standing_frames = []
        for i in range(1, len([name for name in os.listdir("data/images/{}/standing".format(self.game.skin_folder))]) + 1):
            image = pygame.transform.scale(load_image(self.game.skin_folder, "standing", "Idle {}.png".format(str(i))), (60, 90))
            image.set_colorkey(BLACK)
            self.standing_frames.append(image)
        self.walking_frames_r = []
        for i in range(1, len([name for name in os.listdir("data/images/{}/walking".format(self.game.skin_folder))]) + 1):
            image = pygame.transform.scale(load_image(self.game.skin_folder, "walking", "Walk {}.png".format(str(i))), (60, 90))
            image.set_colorkey(BLACK)
            self.walking_frames_r.append(image)
        self.walking_frames_l = [pygame.transform.flip(frame, True, False) for frame in self.walking_frames_r]
        self.jumping_frames_l = []
        for i in range(1, len([name for name in os.listdir("data/images/{}/jumping".format(self.game.skin_folder))]) + 1):
            image = pygame.transform.scale(load_image(self.game.skin_folder, "jumping", "Jump {}.png".format(str(i))), (60, 90))
            image.set_colorkey(BLACK)
            self.jumping_frames_l.append(image)
        self.jumping_frames_r = [pygame.transform.flip(frame, True, False) for frame in self.jumping_frames_l]
        self.powerup_frame_r = pygame.transform.scale(load_image(self.game.skin_folder, "power_up.png"), (60, 120))
        self.powerup_frame_l = pygame.transform.flip(self.powerup_frame_r, True, False)

    def jump(self):
        self.rect.y += 1
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        self.rect.y -= 1
        if self.jumping and not self.double_jump and not self.powering:
            self.game.jump_sound.play()
            self.jumping = True
            self.double_jump = True
            self.velocity.y = -(PLAYER_JUMP - PLAYER_JUMP // 4)
        if hits and not self.jumping:
            self.game.jump_sound.play()
            self.jumping = True
            self.velocity.y = -PLAYER_JUMP

    def jump_cut(self):
        if self.jumping and self.velocity.y < -3:
            self.velocity.y = -3

    def update(self):
        self.animate()
        self.acceleration = vector(0, PLAYER_GRAV)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.acceleration.x = -PLAYER_ACC
        if keys[pygame.K_RIGHT]:
            self.acceleration.x = PLAYER_ACC

        if self.velocity.y >= 0:
            self.powering = False


        self.acceleration.x += self.velocity.x * PLAYER_FRICTION
        self.velocity += self.acceleration
        # Из-за неточностей ноль выставляется автоматически
        if abs(self.velocity.x) < 0.1:
            self.velocity.x = 0
        self.pos += self.velocity + 0.5 * self.acceleration
        if self.pos.x > WIDTH + self.rect.width // 2:
            self.pos.x = 0 - self.rect.width // 2
        if self.pos.x < 0 - self.rect.width // 2:
            self.pos.x = WIDTH + self.rect.width // 2

        self.rect.midbottom = self.pos

    def animate(self):
        now = pygame.time.get_ticks()
        if self.velocity.x != 0 and not self.powering:
            self.walking = True
        else:
            self.walking = False
        if self.powering:
            if self.velocity.x >= 0:
                self.image = self.powerup_frame_r
            else:
                self.image = self.powerup_frame_l
        if self.jumping:
            if now - self.last_update > 60:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.jumping_frames_r)
                bottom = self.rect.bottom
                if self.velocity.x > 0:
                    self.image = self.jumping_frames_l[self.current_frame]
                else:
                    self.image = self.jumping_frames_r[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if self.walking:
            if now - self.last_update > 60:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walking_frames_r)
                bottom = self.rect.bottom
                if self.velocity.x > 0:
                    self.image = self.walking_frames_r[self.current_frame]
                else:
                    self.image = self.walking_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if not self.jumping and not self.walking and not self.powering:
            if now - self.last_update > 150:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        self.mask = pygame.mask.from_surface(self.image)


class Platform(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pygame.transform.scale(load_image("platform.png"), (100, 40))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        if randrange(100) < ACCELERATOR_SPAWN_CHANGE:
            Accelerator(self.game, self)


class Cloud(pygame.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_sprites, game.clouds
        super().__init__(*self.groups)
        self.game = game
        self.image = pygame.transform.scale(choice(game.clouds_images), (randrange(75, 125), randrange(15, 65)))
        self.rect = self.image.get_rect()
        self.rect.x = randrange(WIDTH - self.rect.width)
        self.rect.y = randrange(-500, -50)

    def update(self):
        if self.rect.top > HEIGHT:
            self.kill()


class Accelerator(pygame.sprite.Sprite):
    def __init__(self, game, platform):
        self.groups = game.all_sprites, game.powerups
        super().__init__(*self.groups)
        self.game = game
        self.platform = platform
        self.type = choice(["boost"])
        self.image = pygame.transform.scale(load_image("peas.png"), (20, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = self.platform.rect.centerx
        self.rect.bottom = self.platform.rect.top - 5

    def update(self):
        self.rect.bottom = self.platform.rect.top - 5
        if not self.game.platforms.has(self.platform):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game):
        self.groups = game.all_sprites, game.enemies
        super().__init__(*self.groups)
        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.flying_frames_r[0]
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        self.vx = randrange(1, 4)
        if self.rect.centerx == WIDTH + 100:
            self.image = self.flying_frames_l[0]
            self.vx *= -1
        self.rect.y = randrange(HEIGHT // 2)
        self.vy = 0
        self.dy = 0.5

    def load_images(self):
        self.flying_frames_r = []
        for i in range(1, 9):
            image = pygame.transform.scale(load_image("enemies", "pigeon", "Fly {}.png".format(str(i))), (60, 30))
            image.set_colorkey(BLACK)
            self.flying_frames_r.append(image)
        self.flying_frames_l = [pygame.transform.flip(frame, True, False) for frame in self.flying_frames_r]

    def update(self):
        self.animate()
        self.rect.x += self.vx
        self.vy += self.dy
        if self.vy > 3 or self.vy < 3:
            self.dy *= -1
        self.rect.y += self.vy
        if self.rect.left > WIDTH + 100 or self.rect.left < -100:
            self.kill()

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 150:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.flying_frames_r)
            center = self.rect.center
            if self.vx > 0:
                self.image = self.flying_frames_r[self.current_frame]
            else:
                self.image = self.flying_frames_l[self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.center = center
        self.mask = pygame.mask.from_surface(self.image)
