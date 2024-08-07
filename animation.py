import pygame as pg
import random
from os import path

from settings import *
from sprites import *

class Animation():
	def __init__(self, game):
		self.game = game

	def events(self):
		# events
		for event in pg.event.get():
			if event.type == pg.QUIT:
				if self.game.playing:
					self.game.playing = False
				self.game.running = False
			if event.type == pg.KEYUP:
				if event.key == pg.K_p:
					self.game.boy = 0
					pg.mixer.music.fadeout(500)
					self.game.playing = True
				elif event.key == pg.K_b:
					self.game.boy = 1
					pg.mixer.music.fadeout(500)
					self.game.playing = True
				elif not self.game.first_launch:
					pg.mixer.music.fadeout(500)
					self.game.playing = True

	def update(self):
		# updates
		self.game.all_sprites.update()
		self.game.timer = pg.time.get_ticks()
		if self.game.timer - self.game.now > 3000:
			self.game.start_tag = True

		self.intro_phys(self.game.p1)
		self.intro_phys(self.game.p2)

		# Tag game
		if self.game.start_tag:
			if self.game.tag:
				if not self.game.p1.jumping:
					self.game.p1.vel.x = ANIMATED_SPEED
				if not self.game.p2.jumping:
					self.game.p2.vel.x = ANIMATED_SPEED - random.randrange(1, 2)
				if self.game.p1.rect.right > self.game.p2.rect.left and self.game.p1.rect.right < self.game.p2.rect.right and abs(self.game.p1.pos.y - self.game.p2.pos.y) < 10:
					self.game.p2.vel.x = 0
					self.game.p2.vel.y -= 20
					self.game.p2.jumping = True
					self.game.p1.vel.x = 0
					self.game.p1.pos.x -= 5
					self.game.p1.vel.y -= 7
					self.game.p1.jumping = True
					self.game.tag = False
			else:
				if not self.game.p2.jumping:
					self.game.p2.vel.x = -ANIMATED_SPEED
				if not self.game.p1.jumping:
					self.game.p1.vel.x = -ANIMATED_SPEED + random.randrange(1, 3)
				if self.game.p2.rect.left <= self.game.p1.rect.right and self.game.p2.rect.left >= self.game.p1.rect.left and abs(self.game.p1.pos.y - self.game.p2.pos.y) < 10:
					self.game.p1.vel.x = 0
					self.game.p1.vel.y -= 20
					self.game.p1.jumping = True
					self.game.p2.vel.x = 0
					self.game.p2.pos.x += 5
					self.game.p2.vel.y -= 7
					self.game.p2.jumping = True
					self.game.tag = True
		else:
			if self.game.timer - self.game.now > 1700 and self.game.timer - self.game.now < 2500:
				self.game.p1.image = self.game.p1.walking_frames_r[0]
				self.game.p2.image = self.game.p2.walking_frames_l[0]
			elif self.game.timer - self.game.now > 2500:
				self.game.p1.image =  self.game.p1.standing_frames[0]
				self.game.p2.image =  self.game.p2.standing_frames[0]
		
		
	def intro_phys(self, p):
		# if player lands on plateform
		if p.vel.y > 0 and not p.occupied:
			hits = pg.sprite.spritecollide(p, self.game.plateforms, False)
			if hits:
				lowest = hits[0]
				for hit in hits:
					if hit.rect.centery > lowest.rect.centery:
						lowest = hit
					if p.pos.x < lowest.rect.right + 7 and p.pos.x > lowest.rect.left - 7:
						if p.pos.y < lowest.rect.centery or p.vel.y > 25:
							p.jumping = False
							p.vel.y = 0
							p.pos.y = lowest.rect.top + 2
	def draw(self):
		self.game.window.fill(SKY_BLUE)
		self.game.all_sprites.draw(self.game.window)
		if self.game.first_launch == True:
			self.show_start_screen()
		else:
			self.show_go_screen()

		pg.display.flip()

	def show_start_screen(self):
		#game splash/start screen
		self.game.draw_text(TITLE, SKY_BLUE, 48, WIDTH /2, HEIGHT *0.15)
		self.game.draw_text("Arrows to move", WHITE, 24, WIDTH *0.25, HEIGHT *0.45)
		self.game.draw_text("(going through the left side of the", WHITE, 12, WIDTH *0.25, HEIGHT *0.50)
		self.game.draw_text("screen will make you reappear at the other side)", WHITE, 12, WIDTH *0.25, HEIGHT *0.55)
		self.game.draw_text("Spacebar to jump", WHITE, 24, WIDTH *0.75, HEIGHT *0.50)
		self.game.draw_text("PRESS B to play with Browny", WHITE, 24, WIDTH *1/4, HEIGHT *0.65)
		self.game.draw_text("PRESS P to play with Pinky", WHITE, 24, WIDTH *3/4, HEIGHT *0.65)

	def show_go_screen(self):
		#game over/continue
		if self.game.running:
			self.game.draw_text("GAME OVER !", GRAY, 70, WIDTH /2, HEIGHT * 0.20)
			if self.game.score > self.game.highscore:
				self.game.highscore = self.game.score
				self.game.draw_text("NEW HIGH SCORE!", YELLOW, 42,WIDTH /2, HEIGHT * 0.35)
				with open(path.join(self.game.dir, HS_FILE), 'w') as f:
					f.write(str(self.game.score))
			self.game.draw_text("Score: "+ str(self.game.score), WHITE, 32, WIDTH /2, HEIGHT * 0.45)
			self.game.draw_text("Highscore: "+ str(self.game.highscore), WHITE, 32, WIDTH /2, HEIGHT * 0.50)
			self.game.draw_text("Press any key to play again", WHITE, 32, WIDTH /2, HEIGHT *0.65)
			self.score = 0