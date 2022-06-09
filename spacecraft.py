from fileinput import filename
import random
import time
import threading
import arcade

class Explosion(arcade.Sprite):
    """ This class creates an explosion animation """

    def __init__(self, texture_list):
        super().__init__()
        self.current_texture = 0
        self.textures = texture_list

    def update(self):
        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()

class Spacecraft(arcade.Sprite):
    def __init__(self):
        super().__init__(':resources:images/space_shooter/playerShip1_green.png')
        self.center_x=500
        self.center_y=50
        self.width=50
        self.height=50
        self.speed=4
        self.projectile=arcade.SpriteList()

    def move(self):
        #if self.change_x !=0 and self.change_y !=0:
         #   self.change_x = self.change_x // 3 * 2.12
          #  self.change_y = self.change_y // 3 * 2.12
        self.center_x += self.change_x
        #self.center_y += self.change_y

    def shoot(self):
        self.projectile.append(Fire(self))
        self.projectile[-1].change_y = Fire.speed
        arcade.play_sound(arcade.load_sound(':resources:sounds/laser2.wav'))

class Fire(arcade.Sprite):
    def __init__(self,spacecraft):
        super().__init__()
        self.center_x = spacecraft.center_x
        self.center_y = spacecraft.center_y + 40
        self.width = 5
        self.height = 40
    speed=12
    def draw(self):
        #arcade.draw_circle_filled(self.center_x,self.center_y,6,arcade.color.RED)
        arcade.draw_rectangle_filled(self.center_x,self.center_y,self.width,self.height,arcade.color.BLUE)
    def move(self):
        self.center_y += self.change_y
        

class Enemy(arcade.Sprite):
    def __init__(self, game):
        super().__init__(':resources:images/space_shooter/playerShip2_orange.png',flipped_vertically=True)
        self.center_x = random.randint(0, game.width)
        self.center_y = game.height + 5
        self.width=60
        self.height=60
        self.speed = 2

    def move(self):
        self.center_y -= self.speed

class Game(arcade.Window):
    def __init__(self):
        super().__init__(width=1000,height=690)
        self.image = arcade.load_texture(':resources:images/backgrounds/stars.png')
        self.heart_image = arcade.load_texture('heart.png')
        self.player=Spacecraft()
        self.hearts = 3
        self.score = 0
        self.enemyList = arcade.SpriteList()
        self.explosion_texture_list = []
        self.explosion_texture_list = arcade.load_spritesheet(":resources:images/spritesheets/explosion.png",256,256,16,60)
        self.explosions_list = arcade.SpriteList()
        self.mythread=threading.Thread(target= self.enemyGenerator)
        self.mythread.start()
    
    def on_draw(self):
        if self.hearts == 0:
            self.lose()
            return
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0,0,self.width,self.height,self.image)
        arcade.draw_text('Score: ',self.width-100,20,arcade.color.WHITE,20)
        arcade.draw_text(str(self.score),self.width-30,20,arcade.color.WHITE,20)
        self.explosions_list.draw()
        for i in range(self.hearts):
            arcade.draw_lrwh_rectangle_textured(15+i*45,20,40,40,self.heart_image)
        self.player.draw()
        for a in self.enemyList:
            a.draw()
        for projectile in self.player.projectile:
            projectile.draw()
        

    def on_update(self, delta_time: float):
        if self.hearts == 0:
            self.lose()
            return
        self.player.move()
        self.explosions_list.update()
        for projectile in self.player.projectile:
            projectile.move()
            collision_list = arcade.check_for_collision_with_list(projectile,self.enemyList)
            if len(collision_list) > 0:
                explosion = Explosion(self.explosion_texture_list)
                explosion.center_x = projectile.center_x
                explosion.center_y = projectile.center_y
                explosion.update()
                arcade.play_sound(arcade.load_sound(':resources:sounds/explosion1.wav'))
                self.explosions_list.append(explosion)
                projectile.remove_from_sprite_lists()
                collision_list[0].remove_from_sprite_lists()
                self.score += 1
            if projectile.center_y > self.height:
                self.player.projectile.pop(0)
                #projectile.remove_from_sprite_lists()
        for enemy in self.enemyList:
            enemy.move()
            if enemy.center_y < 0:
                self.hearts -= 1
                arcade.play_sound(arcade.load_sound(':resources:sounds/hurt1.wav'))
                enemy.remove_from_sprite_lists()
        

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RIGHT:
            self.player.texture=arcade.load_texture('right.png')
            self.player.change_x = self.player.speed
        if symbol == arcade.key.LEFT:
            self.player.texture=arcade.load_texture('left.png')
            self.player.change_x = -self.player.speed
        if symbol == arcade.key.UP:
            self.player.change_y = self.player.speed
        if symbol == arcade.key.DOWN:
            self.player.change_y = -self.player.speed
        if symbol == arcade.key.SPACE:
            self.player.shoot()
        if symbol == arcade.key.ENTER and self.hearts == 0:
            self.restart()
        if symbol == arcade.key.ESCAPE and self.hearts == 0:
            self.close()

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RIGHT:
            self.player.texture=arcade.load_texture(':resources:images/space_shooter/playerShip1_green.png')
            self.player.change_x = 0
        if symbol == arcade.key.LEFT:
            self.player.texture=arcade.load_texture(':resources:images/space_shooter/playerShip1_green.png')
            self.player.change_x = 0
        if symbol == arcade.key.UP:
            self.player.change_y = 0
        if symbol == arcade.key.DOWN:
            self.player.change_y = 0

    def enemyGenerator(self):
        while True:
            self.enemyList.append(Enemy(self))
            time.sleep(random.randint(1,5))

    def lose(self):
        self.clear()
        arcade.draw_text('GAME OVER',self.width//2-100,self.height//2+30,arcade.color.ASH_GREY,40)
        arcade.draw_text(f'your score: {self.score}',self.width//2-30,self.height//2-20,arcade.color.ASH_GREY,15)
        arcade.draw_text('press Enter to restart and Esc to quit the game',self.width//2-145,self.height//2-60,arcade.color.ASH_GREY,15)

    def restart(self):
        self.player=Spacecraft()
        self.hearts = 3
        self.score = 0
        self.enemyList = arcade.SpriteList()
        self.mythread.start()
        

mygame=Game()
arcade.run()
    