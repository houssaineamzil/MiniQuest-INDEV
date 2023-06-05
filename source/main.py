import random
import pygame
import pytmx
import math

pygame.init()
pygame.mixer.init()

screenWidth = 800
screenHeight = 800
tileSize = 24
last_shot = 0
gameScreen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("MiniQuest")
villageMap = pytmx.load_pygame("source/tile/village.tmx", pixelalpha=True)
clockObject = pygame.time.Clock()
collision = villageMap.get_layer_by_name("collision")
tiles = []


class Player:
    def __init__(self, x, y):
        playerIMG = pygame.image.load("source/img/player.png")
        self.image = pygame.transform.scale(playerIMG, (tileSize + 12, tileSize * 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3

        self.collision_rect = (
            pygame.Rect(  # Adjust collision box to be smaller than the sprite
                0, 0, self.rect.width * 0.5, self.rect.height * 0.5
            )
        )  # Make the box smaller
        self.collision_rect.midbottom = (
            self.rect.midbottom
        )  # Place it at the bottom center

    def is_collision(self, rect):
        return rect.collidelist(tiles) != -1

    def walk_particles(self):
        if random.random() < 0.2:
            x = self.rect.x + self.image.get_width() // 2
            y = self.rect.y + self.image.get_height()

            velocity_x = random.uniform(-0.2, 0.2)  # Lower velocity values
            velocity_y = random.uniform(-0.2, 0.2)  # Lower velocity values
            color = (
                random.randint(100, 165),
                random.randint(50, 115),
                random.randint(10, 45),
            )  # Brown color

            new_particle = Particle(
                x, y, velocity_x, velocity_y, color, random.randint(2, 6)
            )
            particles.append(new_particle)

    def movement(self):
        key = pygame.key.get_pressed()
        dx, dy = 0, 0  # Changes in x and y
        # Change 'elif' to 'if' for all directions
        if key[pygame.K_a]:
            dx -= 1
        if key[pygame.K_d]:
            dx += 1
        if key[pygame.K_w]:
            dy -= 1
        if key[pygame.K_s]:
            dy += 1

        # Normalize direction vector for consistent speed
        if dx != 0 or dy != 0:
            dist = math.hypot(dx, dy)
            dx, dy = dx / dist, dy / dist  # Normalize the speed
            dx *= self.speed
            dy *= self.speed
            if self.speed != 0:
                self.walk_particles()

        # Draw player
        gameScreen.blit(self.image, self.rect)

        # Check for collisions before updating the player's position
        if dx != 0:  # If there is a change in x
            temp_rect = self.collision_rect.copy()
            temp_rect.x += dx
            if not self.is_collision(temp_rect):
                self.rect.x += dx
                self.collision_rect.x += dx  # Update collision box position

        if dy != 0:  # If there is a change in y
            temp_rect = self.collision_rect.copy()
            temp_rect.y += dy
            if not self.is_collision(temp_rect):
                self.rect.y += dy
                self.collision_rect.y += dy  # Update collision box position


player = Player(400, 700)


class Projectile:
    def __init__(self, start_x, start_y, target_x, target_y, life, speed, owner=None):
        self.owner = owner
        self.image = pygame.image.load(
            "source/img/projectile.png"
        )  # load your projectile image
        self.image = pygame.transform.scale(
            self.image, (20, 20)
        )  # adjust to your desired size

        # calculate the angle from the start to the target position
        dx = target_x - start_x
        dy = target_y - start_y
        self.angle = math.atan2(dy, dx)

        # define a radius for the spawn circle
        spawn_radius = 20  # adjust as necessary

        # calculate the offset position on the spawn circle
        spawn_x = start_x + spawn_radius * math.cos(self.angle)
        spawn_y = start_y + spawn_radius * math.sin(self.angle)

        self.rect = self.image.get_rect()
        self.rect.x = spawn_x
        self.rect.y = spawn_y

        self.speed = speed
        self.collided = False

        self.lifespan = life  # lifespan in frames, adjust as needed

    # update method
    def update(self):
        center_x = self.rect.x + self.image.get_width() // 2
        center_y = self.rect.y + self.image.get_height() // 2

        velocity_x = random.uniform(-1, 1)
        velocity_y = random.uniform(-1, 1)
        color = (255, random.randint(0, 100), 0)  # orange color, you can change it

        new_particle = Particle(
            center_x, center_y, velocity_x, velocity_y, color, random.randint(3, 7)
        )
        particles.append(new_particle)

        # update the position
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)

        # decrease lifespan
        self.lifespan -= 1

        # remove if it leaves the screen or if lifespan is over
        if (
            self.rect.x < 0
            or self.rect.x > screenWidth
            or self.rect.y < 0
            or self.rect.y > screenHeight
        ) or self.lifespan == 0:
            explosions.append(Explosion(self.rect.centerx, self.rect.centery))
            return True

        # remove if it collides with something
        if self.is_collision(self.rect):
            explosions.append(Explosion(self.rect.centerx, self.rect.centery))
            return True

        # draw the projectile
        gameScreen.blit(self.image, self.rect)
        return False

    def is_collision(self, rect):
        return rect.collidelist(tiles) != -1


class Explosion:
    def __init__(self, x, y):
        self.particles = [
            Particle(
                x,
                y,
                (random.uniform(-5, 5)),
                (random.uniform(-5, 5)),
                (random.randint(200, 255), random.randint(50, 150), 0),
                random.randint(3, 7),
            )
            for _ in range(30)
        ]

    def update(self):
        for explosion_particle in self.particles:
            if explosion_particle.update():
                self.particles.remove(explosion_particle)

        # if all particles are gone, the explosion is done
        return len(self.particles) == 0


class Particle:
    def __init__(self, start_x, start_y, velocity_x, velocity_y, color, size):
        self.image = pygame.Surface((size, size))  # adjust to your desired size
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = 0

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        self.lifetime += 2
        alpha = max(255 - self.lifetime * 5, 0)  # decrease by 5 each frame
        self.image.set_alpha(alpha)

        if alpha <= 0:
            return True

        gameScreen.blit(self.image, self.rect)
        return False


def drawGroundLayer2():
    ground_layer = villageMap.get_layer_by_name("ground2")

    for x, y, gid in ground_layer:
        tile = villageMap.get_tile_image_by_gid(gid)
        if tile:
            gameScreen.blit(tile, (x * villageMap.tilewidth, y * villageMap.tileheight))


def drawGroundLayer():
    ground_layer = villageMap.get_layer_by_name("ground")

    for x, y, gid in ground_layer:
        tile = villageMap.get_tile_image_by_gid(gid)
        if tile:
            gameScreen.blit(tile, (x * villageMap.tilewidth, y * villageMap.tileheight))


def drawAboveGroundLayer():
    above_ground_layer = villageMap.get_layer_by_name("above_ground")

    for x, y, gid in above_ground_layer:
        tile = villageMap.get_tile_image_by_gid(gid)
        if tile:
            gameScreen.blit(tile, (x * villageMap.tilewidth, y * villageMap.tileheight))


def collisionSetup():
    for x, y, tile in collision.tiles():
        if tile:
            tiles.append(
                pygame.Rect(
                    [
                        (x * villageMap.tilewidth),
                        (y * villageMap.tileheight),
                        villageMap.tilewidth,
                        villageMap.tileheight,
                    ]
                )
            )


class Enemy:
    def __init__(self, x, y):
        self.original_image = pygame.image.load(
            "source/img/enemy.png"
        )  # Replace with your enemy sprite
        self.image = pygame.transform.scale(
            self.original_image, (tileSize * 3, tileSize * 3)
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 3
        self.hit = False
        self.move_counter = 0  # counter for controlling movement changes
        self.direction = 0  # direction of movement
        self.last_shot = 0  # Add this line
        self.canshoot = True
        self.hit_counter = 0

    def shoot(self, target_x, target_y):
        if self.canshoot:
            current_time = pygame.time.get_ticks()
            if (
                current_time - self.last_shot >= 1000
            ):  # Checks if it's been 1 second (1000 ms) since the last shot
                fireball_sound.play()
                new_projectile = Projectile(
                    self.rect.centerx,
                    self.rect.centery,
                    target_x,
                    target_y,
                    40,
                    15,
                    self,
                )
                projectiles.append(new_projectile)
                self.last_shot = current_time  # Update the last_shot time

    def take_damage(self):
        self.hp -= 1
        self.hit = True
        self.hit_counter = 10

    def draw(self):
        if self.hit_counter > 0:  # Check the hit counter instead of self.hit
            # When the enemy is hit, we'll create a new image with a red tint
            red_image = pygame.Surface(self.image.get_size()).convert_alpha()
            red_image.fill((255, 128, 128))  # Full red, no alpha value
            self.image.blit(red_image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            self.hit_counter -= 1  # Decrement the hit counter

        gameScreen.blit(self.image, self.rect)

        # Reset to original image for next frame
        if self.hit_counter <= 0:  # Check the hit counter instead of self.hit
            self.image = pygame.transform.scale(
                self.original_image, (tileSize * 3, tileSize * 3)
            )
            self.hit = False

    def is_collision(self, rect):
        return rect.collidelist(tiles) != -1

    def update(self):
        if self.move_counter > 0:
            self.move_counter -= 1
            self.move()
        else:
            self.move_counter = 60  # approximately once per second at 60 FPS
            self.direction = random.randint(0, 3)  # choose a random direction

    def move(self):
        speed = 2  # speed of the enemy
        if self.direction == 0:  # up
            temp_rect = self.rect.copy()
            temp_rect.y -= speed
            if not self.is_collision(temp_rect) and temp_rect.y > 0:
                self.rect.y -= speed
        elif self.direction == 1:  # right
            temp_rect = self.rect.copy()
            temp_rect.x += speed
            if not self.is_collision(temp_rect) and temp_rect.x < (
                screenWidth - self.rect.width
            ):
                self.rect.x += speed
        elif self.direction == 2:  # down
            temp_rect = self.rect.copy()
            temp_rect.y += speed
            if not self.is_collision(temp_rect) and temp_rect.y < (
                screenHeight - self.rect.height
            ):
                self.rect.y += speed
        elif self.direction == 3:  # left
            temp_rect = self.rect.copy()
            temp_rect.x -= speed
            if not self.is_collision(temp_rect) and temp_rect.x > 0:
                self.rect.x -= speed


import os

print(os.getcwd())
# Create the enemy
enemy = Enemy(200, 200)  # Replace with the position where you want the enemy to appear
# Load the music file
pygame.mixer.music.load("source/sound/music.wav")
fireball_sound = pygame.mixer.Sound("source/sound/fireball.mp3")
explosion_sound = pygame.mixer.Sound("source/sound/explosion.mp3")

# Play the music indefinitely
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.4)
# Inside your game loop
projectiles = []
particles = []
explosions = []
explosion_particles = []
canshoot = True
run = True
while run:
    clockObject.tick(60)

    tiles = []  # Reset the list of collision tiles
    collisionSetup()  # Update the list of collision tiles

    drawGroundLayer2()
    drawGroundLayer()  # Draw ground layer

    for projectile in projectiles:
        if player.rect.colliderect(projectile.rect) and projectile.owner is not player:
            # Create an explosion effect at the projectile's position
            explosion_particles.extend(
                [
                    Particle(
                        projectile.rect.centerx,
                        projectile.rect.centery,
                        (random.randint(0, 50) - 10) / 10,
                        (random.randint(0, 50) - 10) / 10,
                        (255, 0, 0),
                        random.randint(3, 7),
                    )
                    for _ in range(30)
                ]
            )

            # Disable player movement
            player.speed = 0

            # Remove the projectile
            projectiles.remove(projectile)

            # Stop shooting
            canshoot = False
            enemy.canshoot = False
            red_image = pygame.Surface(player.image.get_size()).convert_alpha()
            red_image.fill((255, 0, 0))
            player.image.blit(red_image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            player.image = pygame.transform.rotate(
                player.image, -90
            )  # rotate 90 degrees clockwise

        if projectile.update():
            explosion_sound.play()
            projectiles.remove(projectile)
        else:
            # Only check for collision if enemy is not None
            if (
                enemy is not None
                and enemy.rect.colliderect(projectile.rect)
                and projectile.owner is not enemy
            ):
                enemy.take_damage()
                explosions.append(
                    Explosion(projectile.rect.centerx, projectile.rect.centery)
                )
                explosion_sound.play()
                projectiles.remove(projectile)
                if enemy.hp <= 0:
                    enemy = None
                    break

    for particle in particles:
        if particle.update():
            particles.remove(particle)

    for explosion in explosions[:]:  # iterate over a copy of the list
        if explosion.update():
            explosions.remove(explosion)

    for particle in explosion_particles[:]:  # iterate over a copy of the list
        if particle.update():
            explosion_particles.remove(particle)

    for particle in explosion_particles:
        particle.update()

    if enemy is not None:
        enemy.update()  # Move the enemy
        enemy.draw()  # Draw the enemy
        enemy.shoot(player.rect.centerx, player.rect.centery)

    player.movement()  # Draw player

    drawAboveGroundLayer()  # Draw above ground layer

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 & canshoot:  # Left mouse button
                current_time = pygame.time.get_ticks()
                if (
                    current_time - last_shot >= 1000
                ):  # Checks if it's been 1 second (1000 ms) since the last shot
                    # Play the fireball sound effect
                    fireball_sound.play()

                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    new_projectile = Projectile(
                        player.rect.centerx,
                        player.rect.centery,
                        mouse_x,
                        mouse_y,
                        25,
                        10,
                        player,
                    )
                    projectiles.append(new_projectile)
                    last_shot = current_time  # Update the last_shot time

    pygame.display.update()

pygame.quit()
