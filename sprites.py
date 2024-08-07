from random import choice, randrange
import pygame as pg
vec = pg.math.Vector2

from settings import *

class Spritesheet:
	# Utility class for loading and parsing the spritesheet
	def __init__(self, filename):
		self.spritesheet = pg.image.load(filename).convert()

	def get_image(self, x, y, width, height, scale = 0):
		#grab image out of a larger spritesheet
		image = pg.Surface((width, height))
		image.blit(self.spritesheet, (0, 0), (x, y, width, height))
		if scale == 0:
			image = pg.transform.scale(image, (width //2, height //2))
		else:
			image = pg.transform.scale(image, (int(width *scale), int(height *scale)))
		return image

class Cloud(pg.sprite.Sprite):
	def __init__(self, game):
		if game.score > 4500:
			self._layer = choice([CLOUD_LAYER, PLAYER_LAYER + 1])
		else:
			self._layer = CLOUD_LAYER 
		self.groups = game.all_sprites, game.clouds
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = choice(self.game.cloud_images)
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		scale = randrange(50, 100) / 100
		self.image = pg.transform.scale(self.image,(int(self.rect.width *scale),
													int(self.rect.height * scale)))
		if self.game.score < 6000:
			self.rect.centerx = randrange(WIDTH - self.rect.width)
			self.rect.centery = randrange(-500, -50)
		else:
			self.rect.centerx = 0 - self.rect.width
			self.rect.centery = WIDTH + randrange(-500, -50)
		self.last_update = 0
		self.delay = randrange(50, 300)
		self.speedx = 2
	
	def update(self):
		now = pg.time.get_ticks()
		if now - self.last_update > self.delay:
			self.last_update = now
			self.rect.centerx += self.speedx
		if self.rect.left > WIDTH + 5:
			self.rect.right = -50
			self.rect.centery = randrange(HEIGHT * 1/2)
		if self.rect.top > HEIGHT + 50:
			self.kill()
		
class Player(pg.sprite.Sprite):
	def __init__(self, game):
		self._layer = PLAYER_LAYER
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.boy = game.boy
		self.walking = False
		self.jumping = False
		self.jet = False
		self.occupied = False
		self.fuel = 0
		self.current_frame = 0
		self.last_change = 0
		self.load_images()
		self.image = self.standing_frames[0]
		self.rect = self.image.get_rect()
		self.rect.bottom = HEIGHT
		self.rect.centerx = WIDTH /2
		if bool(game.boy):
			self.pos = vec(WIDTH * 0.2, int(HEIGHT * 0.9))
		else:
			self.pos = vec(WIDTH * 0.7, int(HEIGHT * 0.9))

		self.vel = vec(0, 0)
		self.acc = vec(0, 0)
	
	def load_images(self):
		if bool(self.boy):
			self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
									self.game.spritesheet.get_image(690, 406, 120, 201)]
			for frame in self.standing_frames:
				frame.set_colorkey(BLACK)
			self.walking_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201), 
									self.game.spritesheet.get_image(692, 1458, 120, 207)]
			self.walking_frames_l = []
			for frame in self.walking_frames_r:
				frame.set_colorkey(BLACK)
				self.walking_frames_l.append(pg.transform.flip(frame, True, False))
			self.jumping_frame = self.game.spritesheet.get_image(382, 763, 150, 181)
			self.jumping_frame.set_colorkey(BLACK)
		else:
			self.standing_frames = [self.game.spritesheet.get_image(581, 1265, 121, 191),
									self.game.spritesheet.get_image(584, 0, 121, 201)]
			for frame in self.standing_frames:
				frame.set_colorkey(BLACK)
			self.walking_frames_r = [self.game.spritesheet.get_image(584, 203, 121, 201), 
									self.game.spritesheet.get_image(678, 651, 121, 207)]
			self.walking_frames_l = []
			for frame in self.walking_frames_r:
				frame.set_colorkey(BLACK)
				self.walking_frames_l.append(pg.transform.flip(frame, True, False))
			self.jumping_frame = self.game.spritesheet.get_image(416, 1660, 150, 181)
			self.jumping_frame.set_colorkey(BLACK)
	
	def animate(self):
		now = pg.time.get_ticks()
		if abs(self.vel.x) < 1.5:
			self.walking = False
		else:
			self.walking = True
		if not self.occupied:
			if self.jumping:
				bottom = self.rect.bottom
				self.image = self.jumping_frame
				self.rect = self.image.get_rect()
				self.rect.bottom = bottom

			elif self.walking and (now - self.last_change) > 120:
				self.last_change = now
				self.current_frame = (self.current_frame + 1) % len(self.walking_frames_r)
				bottom = self.rect.bottom
				if self.vel.x > 0:
					self.image = self.walking_frames_r[self.current_frame]
				else:
					self.image = self.walking_frames_l[self.current_frame]
				self.rect = self.image.get_rect()
				self.rect.bottom = bottom
			elif not self.walking and not self.jumping:
				if now - self.last_change > 400:
					self.last_change = now
					self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
					bottom = self.rect.bottom
					self.image = self.standing_frames[self.current_frame]
					self.rect = self.image.get_rect()
					self.rect.bottom = bottom
		elif self.jet:
			if self.boy:
				self.image = self.game.jettedb
			else:
				self.image = self.game.jettedp
		self.mask = pg.mask.from_surface(self.image)

	def jump(self):
		if not self.occupied:
			self.rect.y += 2
			hit = pg.sprite.spritecollide(self.game.player, self.game.plateforms, False)
			if hit and self.jumping == False:
				self.game.jump_snd.play()
				self.jumping = True
				self.vel.y -= PLAYER_JUMP
			self.rect.y -= 2
	
	def jump_cut(self):
		if self.jumping:
			if abs(self.vel.y) < PLAYER_JUMP:
				if self.vel.y < 0:
					self.vel.y = 0

	def die(self):
		self.occupied = True
		center = self.rect.center
		if bool(self.boy):
			self.image = self.game.spritesheet.get_image(382, 946, 150, 174)
		else:
			self.image = self.game.spritesheet.get_image(411, 1866, 150, 174)
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.vel.y = -10
		self.fuel = 0
		self.jet = False

	def update(self):
		self.animate()
		if not self.jet:
			if self.vel.y < MAX_SPEED_UP:
				self.vel.y = MAX_SPEED_UP
			elif self.vel.y > MAX_SPEED_DOWN:
				self.vel.y = MAX_SPEED_DOWN
		else:
			self.fuel -= 1
			self.vel.y = JET_SPEED
		self.acc = vec(0, PLAYER_GRAV)
		keys = pg.key.get_pressed()
		if keys[pg.K_LEFT]:
			self.acc.x = -PLAYER_ACC
		if keys[pg.K_RIGHT]:
			self.acc.x = PLAYER_ACC

		# Apply friction
		self.acc.x += self.vel.x * PLAYER_FRICTION

		# Equation of motion
		self.vel += self.acc
		if abs(self.vel.x) < 0.6:
			self.vel.x = 0
		self.pos += self.vel + (self.acc /2)
		if self.pos.x < 0 - (self.rect.width /2):
			self.pos.x = WIDTH
		if self.pos.x > WIDTH + (self.rect.width /2):
			self.pos.x = 0

		self.rect.midbottom = self.pos

class Plateform(pg.sprite.Sprite):
	def __init__(self, game, x, y, scale = 0):
		self._layer = PLATFORM_LAYER
		self.groups = game.all_sprites, game.plateforms
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		if scale:
			images = [self.game.spritesheet.get_image(0, 288, 380, 94, scale)]
		else:
			images = [self.game.spritesheet.get_image(0, 288, 380, 94),
				self.game.spritesheet.get_image(213, 1662, 201, 100)]
		self.image = choice(images)
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)

class Pow(pg.sprite.Sprite):
	def __init__(self, game, plat):
		self._layer = POW_LAYER
		self.groups = game.all_sprites, game.pows
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.plat = plat
		self.spring_in = self.game.spritesheet.get_image(0, 1988, 145, 57)
		self.spring_out = self.game.spritesheet.get_image(434, 1265, 145, 110)
		self.image = self.spring_in
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.bottom = self.plat.rect.top
		self.rect.centerx = self.plat.rect.centerx
		self.used = False
	
	def spring(self):
		self.used = True
		bottom = self.rect.bottom
		self.image = self.spring_out
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.bottom = bottom
		self.rect.centerx = self.plat.rect.centerx
		self.kill()

	def update(self):
		self.rect.bottom = self.plat.rect.top
		if not self.game.plateforms.has(self.plat):
			self.kill()

class Jet(pg.sprite.Sprite):
	def __init__(self, game, plat):
		self._layer = POW_LAYER
		self.groups = game.all_sprites, game.jets
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.plat = plat
		self.image = self.game.spritesheet.get_image(563, 1843, 133, 160)
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.bottom = self.plat.rect.top - 10
		self.rect.centerx = self.plat.rect.centerx
		self.last_update = 0
		self.used = False

	def update(self):
		self.rect.bottom = self.plat.rect.top + 10
		if not self.game.plateforms.has(self.plat):
			self.kill()

class Mob(pg.sprite.Sprite):
	def __init__(self, game):
		self._layer = MOB_LAYER
		self.groups = game.all_sprites, game.mobs
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.images = [self.game.spritesheet.get_image(566, 510, 122, 139),
								self.game.spritesheet.get_image(568, 1534, 122, 135)]
		for image in self.images:
			image.set_colorkey(BLACK)
		self.image = self.images[1]
		self.rect = self.image.get_rect()
		y = randrange(HEIGHT * 1/4, HEIGHT * 3/4)
		x = choice([-50, WIDTH + 50])
		self.rect.center = (x, y)
		self.vx = randrange(1, 4)
		if x > 0:
			self.vx *= -1
		self.vy = 0
		self.ay = 0.5
	
	def update(self):
		#Going up and down
		self.rect.x += self.vx
		if self.vy > 3 or self.vy < -3:
			self.ay *= -1
			center = self.rect.center
			if self.ay < 0:
				self.image = self.images[0]
			else:
				self.image = self.images[1]
			self.rect = self.image.get_rect()
			self.rect.center = center
		self.vy += self.ay
		self.rect.y += self.vy
		if self.rect.x < -100 or self.rect.x > HEIGHT + 100:
			self.kill()
		self.mask = pg.mask.from_surface(self.image)

class Spike(pg.sprite.Sprite):
	def __init__(self, game, plat):
		self._layer = MOB_LAYER
		self.groups = game.all_sprites, game.spikes
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.plat = plat
		self.walking = False
		self.last_animated = 0
		self.last_update = 0
		self.load_images()
		self.sequence = 0
		self.current_frame = 0
		self.image = self.standing_frame
		self.rect = self.image.get_rect()
		self.rect.bottom = self.plat.rect.top
		self.rect.centerx = self.plat.rect.centerx
		self.original_pos = self.rect.centerx
		self.vx = 0

	def animate(self):
		now = pg.time.get_ticks()
		if self.walking and (now - self.last_animated) > 200:
			self.last_animated = now
			self.current_frame = (self.current_frame + 1) % len(self.walking_frames_r)
			bottom = self.rect.bottom
			if self.vx > 0:
				self.image = self.walking_frames_r[self.current_frame]
			else:
				self.image = self.walking_frames_l[self.current_frame]
			#self.rect = self.image.get_rect()
			#self.rect.bottom = bottom
		elif not self.walking:
				bottom = self.rect.bottom
				self.image = self.standing_frame
			#	self.rect = self.image.get_rect()
			#	self.rect.bottom = bottom
		self.mask = pg.mask.from_surface(self.image)

	def load_images(self):
		self.standing_frame = self.game.spritesheet.get_image(814, 1417, 90, 155)
		self.standing_frame.set_colorkey(BLACK)
		self.walking_frames_r = [self.game.spritesheet.get_image(704, 1256, 120, 159), 
								self.game.spritesheet.get_image(812, 296, 90, 155)]
		self.walking_frames_l = []
		for frame in self.walking_frames_r:
			frame.set_colorkey(BLACK)
			self.walking_frames_l.append(pg.transform.flip(frame, True, False))


	def update(self):
		self.animate()
		now = pg.time.get_ticks()
		self.rect.bottom = self.plat.rect.top
		if not self.game.plateforms.has(self.plat):
			self.kill()
		if (now - self.last_update) > 3000 and self.sequence == 0:
			self.vx = 2
			self.sequence += 1
			self.walking = True
		elif (self.rect.right > self.plat.rect.right - 5 or self.rect.right > WIDTH - 5) and self.sequence == 1:
			self.vx = 0
			self.sequence += 1
			self.last_update = now
			self.walking = False
		elif (now - self.last_update) > 2000 and self.sequence == 2:
			self.vx = -2
			self.sequence += 1
			self.walking = True
		elif self.rect.centerx == self.original_pos and self.sequence == 3:
			self.vx = 0
			self.sequence += 1
			self.last_update = now
			self.walking = False
		elif (now - self.last_update) > 2000 and self.sequence == 4:
			self.vx = -2
			self.sequence += 1
			self.walking = True
		elif (self.rect.left < self.plat.rect.left + 5 or self.rect.right < 5) and self.sequence == 5 :
			self.vx = 0
			self.sequence += 1
			self.last_update = now
			self.walking = False
		elif (now - self.last_update) > 2000 and self.sequence == 6:
			self.vx = 2
			self.sequence += 1
			self.walking = True
		elif self.rect.centerx > self.original_pos and self.sequence == 7:
			self.vx = 0
			self.sequence = 0
			self.last_update = now
			self.walking = False
		self.rect.x += self.vx