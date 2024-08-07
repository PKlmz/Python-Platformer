# Jumping to the stars - platform game
import pygame as pg
from os import path
import random

from settings import *
from sprites import *
from animation import *

class Game:
	def __init__(self):
		#initialize game window, etc
		pg.init()
		pg.mixer.init()
		self.window = pg.display.set_mode(resolution)
		pg.display.set_caption(TITLE)
		self.clock = pg.time.Clock()
		self.running = True
		self.first_launch = True
		self.font_name = pg.font.match_font(FONT_NAME)

		self.animation = Animation(self)

		self.load_data()
	
	def load_data(self):
		self.boy = 1
		self.score = 0

		self.dir = path.dirname(__file__)
		img_dir = path.join(self.dir, 'img')
		
		with open(path.join(self.dir, HS_FILE), 'r') as f:
			try:
				self.highscore = int(f.read())
			except:
				self.highscore = 0
		
		# load spritesheet
		self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
		self.jettedb = pg.image.load(path.join(img_dir, 'jettedb.png')).convert()
		self.jettedb = pg.transform.scale(self.jettedb, (75, 135))
		self.jettedb.set_colorkey(BLACK)
		self.jettedp = pg.image.load(path.join(img_dir, 'jettedp.png')).convert()
		self.jettedp = pg.transform.scale(self.jettedp, (75, 135))
		self.jettedp.set_colorkey(BLACK)

		# load sounds
		self.snd_dir = path.join(self.dir, 'snd')
		self.jump_snd = pg.mixer.Sound(path.join(self.snd_dir, 'jump_snd.ogg'))
		self.boost_snd = pg.mixer.Sound(path.join(self.snd_dir, 'boost_snd.wav'))
		self.hurt_snd = pg.mixer.Sound(path.join(self.snd_dir, 'hurt_snd.wav'))
		self.jet_snd = pg.mixer.Sound(path.join(self.snd_dir, 'jet_snd.wav'))

		# load_clouds
		self.cloud_images = []
		for i in range (1, 4):
			self.cloud_images.append(pg.image.load(path.join(img_dir, 'cloud{}.png'.format(i))).convert())
	
	def new_animation(self):
		# new
		self.all_sprites = pg.sprite.LayeredUpdates()
		self.clouds = pg.sprite.Group()
		self.plateforms = pg.sprite.Group()

		self.start_tag = False
		self.timer = pg.time.get_ticks()
		self.now = self.timer
		boy = self.boy
		self.boy = 1
		self.p1 = Player(self)
		self.boy = 0
		self.p2 = Player(self)
		self.boy = boy
		if bool(boy):
			if not self.first_launch:
				self.p1.pos = vec(WIDTH * 0.2, int(HEIGHT * 0.05))
		else:
			self.p2.pos = vec(WIDTH * 0.7, int(HEIGHT * 0.05))

		self.tag = True
		for i in range (40):
			c = Cloud(self)
			c.rect.y += 350

		Plateform(self, WIDTH/2, HEIGHT * 1.05, 2)
		self.new_intro = 1

	def new(self):
		# start a new game
		self.red_d = 0
		self.green_d = 0
		self.blue_d = 110
		self.show_d = 1
		self.red_g = 100
		self.green_g = 100
		self.blue_g = 255
		self.red_n = 20
		self.blue_n = 40

		self.window_color = (0, 0, 120)

		self.star_count = 0
		self.stars = []

		self.score = 0
		self.last_score = 0
		self.mob_timer = 0
		self.boosted = False
		self.fuel_image = self.spritesheet.get_image(820, 1805, 71, 70)
		self.fuel_image.set_colorkey(BLACK)

		self.red = 100
		self.green = 100
		self.blue = 255 

		self.all_sprites = pg.sprite.LayeredUpdates()
		self.clouds = pg.sprite.Group()
		self.plateforms = pg.sprite.Group()
		self.jets = pg.sprite.Group()
		self.pows = pg.sprite.Group()
		self.mobs = pg.sprite.Group()
		self.spikes = pg.sprite.Group()
		self.player = Player(self)

		for plat in PLATFORM_LIST:
			Plateform(self, *plat)
		for i in range (8):
			c = Cloud(self)
			c.rect.y += 500

	def run(self):
		#Game loop
		self.playing = False
		pg.mixer.music.load(path.join(self.snd_dir, 'Caketown_ms.ogg'))
		pg.mixer.music.play(loops=-1)
		self.new_animation()
		while not self.playing and self.running:
			self.clock.tick(FPS)
			self.animation.events()
			self.animation.update()
			self.animation.draw()
		self.first_launch = False
		self.new()
		pg.mixer.music.load(path.join(self.snd_dir, 'happy_ms.ogg'))
		pg.mixer.music.play(loops=-1)
		while self.playing and self.running:
			self.clock.tick(FPS)
			self.events()
			self.update()
			self.draw()
		pg.mixer.music.fadeout(500)
			
	def update(self):
		#Game loop - Update		
		self.all_sprites.update()
		
		# if player hits mob
		hits = pg.sprite.spritecollide(self.player, self.mobs, False, pg.sprite.collide_mask)
		if hits and not self.player.occupied:
			self.hurt_snd.play()
			self.player.die()
		
		hit_spikes = pg.sprite.spritecollide(self.player, self.spikes, False, pg.sprite.collide_mask)
		if hit_spikes and not self.player.occupied and not self.player.jet:
			for hit in hit_spikes:
				if abs(self.player.vel.y) > 1 and self.player.rect.centery < hit.rect.centery:
					if (self.player.rect.centerx <= hit.rect.centerx and self.player.rect.left < hit.rect.right - hit.rect.width /3) or (self.player.rect.centerx >= hit.rect.centerx and self.player.rect.right > hit.rect.left - hit.rect.width /3):
						self.hurt_snd.play()
						self.player.die()
			
		# if player hits powerup
		pow_hits = pg.sprite.spritecollide(self.player, self.pows, False)
		if pow_hits and not self.player.occupied:
			if not pow_hits[0].used:
				self.player.jumping = True
				self.boosted = True
				self.jump_snd.play()
				pow_hits[0].spring()
				self.player.vel.y = -BOOST_POWER
		
		jet_hits = pg.sprite.spritecollide(self.player, self.jets, False)  
		if jet_hits and not self.player.occupied:
			if not self.boosted and not self.player.occupied:
				self.jetpack = jet_hits[0]
				self.player.fuel = MAX_FUEL
				self.player.jumping = True
				self.player.occupied = True
				self.player.vel.y = JET_SPEED
				self.boosted = True
				self.player.jet = True
		elif jet_hits and self.player.jet:
			self.player.fuel += MAX_FUEL /2

		# if player lands on plateform
		if self.player.vel.y > 0 and not self.player.occupied:
			hits = pg.sprite.spritecollide(self.player, self.plateforms, False)
			if hits:
				lowest = hits[0]
				for hit in hits:
					if hit.rect.centery > lowest.rect.centery:
						lowest = hit
					if self.player.pos.x < lowest.rect.right + 7 and self.player.pos.x > lowest.rect.left - 7:
						if self.player.pos.y < lowest.rect.centery or self.player.vel.y > 25:
							self.player.jumping = False
							self.player.vel.y = 0
							self.player.pos.y = lowest.rect.top + 2

		# if player reaches top 1/4 of the window
		if self.player.pos.y - (self.player.rect.height /2) < HEIGHT /4:
			self.player.pos.y += max(abs(self.player.vel.y), 4)
			if self.score < 8000 and random.randrange(100) < 10:
				if 4500 < self.score < 6000:
					Cloud(self)
				if self.score < 6000:
					Cloud(self)
				else:
					if random.choice([True, False]):
						Cloud(self)
			for cloud in self.clouds:
				cloud.rect.y += max(abs(int(self.player.vel.y /randrange(1, 4))), 2)
			for plat in self.plateforms:
				plat.rect.y += max(abs(self.player.vel.y), 6)
				if plat.rect.y >= HEIGHT + 50:
					self.score += 10
					plat.kill()
			for mob in self.mobs:
				mob.rect.y += max(abs(self.player.vel.y), 6)
				if mob.rect.y >= HEIGHT + 50:
					mob.kill()
		
		# Spawn mob
		now = pg.time.get_ticks()
		if (now - self.mob_timer) > max(12000 - self.score, 3000) + random.choice([-500, 0, 500]) and self.score > 4000:
			self.mob_timer = now
			Mob(self)
		
		# Keep average plateform number + spawn mobs/powerups
		highest = HEIGHT
		for plat in self.plateforms:
			if plat.rect.centery < highest:
				highest = plat.rect.centery
		if highest > HEIGHT * 0.01:
			x = random.randrange(10, WIDTH - 10)
			y = highest - int(WIDTH * random.choice([0.15, 0.20, 0.25]))
			p = Plateform(self, x, y)
			if self.score > 0:
				if self.score > 500 and randrange(100) < POW_SPAWN_PCT:
					if self.score < 9500:
						Pow(self, p)
					else:
						Jet(self, p)
				elif self.score > 1500 and randrange(100) < SPIKE_SPAWN_PCT:
					Spike(self, p)
				elif self.score > 2500 and random.randrange(100) < JET_SPAWN_PCT:
					if self.score < 9500:
						Jet(self, p)
					else:
						Pow(self, p)
			if random.randrange(8) == 1:
				y2 = highest - int(WIDTH *0.25)
				if y2 == y:
					if x > WIDTH /2:
						x = p.rect.left - random.randrange(400, 550)
					else:
						x = p.rect.right + random.randrange(400, 550)
				else:
					x = random.randrange(10, WIDTH - 10)
				p2 = Plateform(self, x, y)
				if self.score > 0:
					if random.randrange(100) < POW_SPAWN_PCT:
						if self.score < 9500:
							Pow(self, p2)
						else:
							Jet(self, p2)
					elif random.randrange(100) < SPIKE_SPAWN_PCT:
						Spike(self, p2)
					elif random.randrange(100) < JET_SPAWN_PCT:
						if self.score < 9500:
							Jet(self, p2)
						else:
							Pow(self, p2)


		# Die ?
		if self.player.pos.y > HEIGHT:
			for sprite in self.all_sprites:
				sprite.rect.y -= self.player.vel.y
				if sprite.rect.bottom < 0:
					sprite.kill()
				if len(self.plateforms) == 0:
					self.playing = False
		
		# Swap jet-packs to fuel boosts
		if self.player.jet:
			for jets in self.jets:
				if not jets.image == self.spritesheet.get_image(820, 1805, 71, 70):
					jets.image = self.spritesheet.get_image(820, 1805, 71, 70)
					jets.image.set_colorkey(BLACK)
		else:
			for jets in self.jets:
				if not jets.image == self.spritesheet.get_image(563, 1843, 133, 160):
					jets.image = self.spritesheet.get_image(563, 1843, 133, 160)
					jets.image.set_colorkey(BLACK)

		# remove boosted protection
		if self.boosted:
			self.player.occupied = True
			if self.player.vel.y > 0:
				self.boosted = False
				self.player.occupied = False
			if self.player.fuel <= 0 and self.player.jet:
				self.player.jet = False
				self.boosted = False
				self.player.occupied = False
				self.jetpack.kill()

	def events(self):
		#Game loop - Events
		for event in pg.event.get():
			if event.type == pg.QUIT:
				if self.playing:
					self.playing = False
				self.running = False
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_SPACE:
					self.player.jump()
			if event.type == pg.KEYUP:
				if event.key == pg.K_SPACE:
					self.player.jump_cut()

	def degrade(self, red, green, blue, red_var, green_var, blue_var):
		x = 0
		red = red - red_var
		green = green - green_var
		blue = blue - blue_var
		if self.score < 8000:
			self.window.fill(GRAY)
		else:
			self.window.fill(NIGHT_PURPLE)
		while not x == 56:
			rect = [0, int(HEIGHT * x /100 + max((self.sunset - 2500)* 0.4, 0)), WIDTH, HEIGHT /10]
			if x <= self.show_d:
				pg.draw.rect(self.window, (max(min(red + x * 3, 200), 20), max(min(green + x* 3, 200), 0), max(min(blue + x * 7/2, 200), 40)), rect)
			x += 1
		red = min(red + x * 3, 200)
		green = min(green + x* 3, 200)
		blue = min(blue + x * 7/2, 200)
		while not x == 60:
			x += 1
		while not x == 100:
			y = x - 60
			rect = [0, int(HEIGHT * x /100 + max((self.sunset - 2500)*0.45, 0)), WIDTH, HEIGHT/10]
			if x <= self.show_d:
				pg.draw.rect(self.window, (max(min(red + y *2.5, 255), 20), max(min(green + y * 0.5, 255), 0), min(max(blue - y * 7.5, 40), 255)), rect)
			x += 1
		if self.show_d < 101:
			self.show_d = (self.score - 6000) / 10

	def gray_sky(self):
		diff = self.score - self.last_score - 4500
		if not self.red_g == 170 or not self.green_g == 170 or not self.blue_g == 170:
			if self.red_g < 170:
				self.red_g += diff /10
			elif self.red_g > 170:
				self.red_g -= diff /10
			if self.green_g < 170:
				self.green_g += diff /10
			elif self.green_g > 170:
				self.green_g -= diff /10
			if self.blue_g < 170:
				self.blue_g += diff /10
			elif self.blue_g > 170:
				self.blue_g -= diff /10
		self.last_score += diff
		self.window.fill((self.red_g, self.green_g, self.blue_g))

	def fade_toblack(self):
		diff = self.score - self.last_score - 9700
		if not self.red_n == 0 or not self.blue_n == 0:
			if self.red_n > 0:
				self.red_n -= diff /10
			if self.blue_n > 0:
				self.blue_n -= diff /10
		if self.star_count <= 300 and bool(diff):
			self.add_star()
		self.last_score += diff
		self.window.fill((max(self.red_n, 0), 0, max(self.blue_n, 0)))
		for i in self.stars:
			pg.draw.rect(self.window, WHITE, i)

	def add_star(self):
		x = random.randrange(0, WIDTH)
		y = random.randrange(0, HEIGHT)
		size = random.randrange(1, 3)
		rect = [x, y, size, size]
		self.stars.append(rect)
		self.star_count += 1

	def skychanges(self):
		if self.score > 9700:
			self.fade_toblack()
		elif self.score > 6000:
			self.sunset = self.score - 6000
			self.degrade(self.red_d, self.green_d, self.blue_d, self.sunset //20, self.sunset //20, self.sunset //20)
			self.last_score = 0
		elif self.score > 4500:
			self.gray_sky()
		else:
			self.window.fill(SKY_BLUE)

	def draw(self):
		#Game loop - Draw
		self.skychanges()
		self.all_sprites.draw(self.window)
		self.draw_text(str(self.score), WHITE, 24, WIDTH /2, HEIGHT *0.01)
		if self.player.jet:
			self.draw_fuel()
		pg.display.flip()
	
	def draw_fuel(self):
		img_rect = self.fuel_image.get_rect()
		img_rect.x = 5
		img_rect.y = 5
		if self.player.fuel < 0:
			self.player.fuel = 0
		if self.player.fuel > MAX_FUEL:
			self.player.fuel = MAX_FUEL

		fuel = (self.player.fuel /MAX_FUEL) * FUELBAR_WIDTH
		outside_rect = pg.Rect(45, 10, FUELBAR_WIDTH, FUELBAR_HEIGHT)
		fill_rect = pg.Rect(45, 10, fuel, FUELBAR_HEIGHT)
		if self.player.fuel > MAX_FUEL * 2/3:
			color = GREEN
		elif self.player.fuel > MAX_FUEL * 1/3:
			color = YELLOW
		else:
			color = RED
		pg.draw.rect(self.window, color, fill_rect)
		pg.draw.rect(self.window, WHITE, outside_rect, 2)
		self.window.blit(self.fuel_image, img_rect)

	def wait_key(self):
		waiting = True
		while waiting:
			for event in pg.event.get():
				if event.type == pg.QUIT:
					waiting = False
					self.running = False
				elif event.type == pg.KEYUP:
					waiting = False

	def draw_text(self, text, color, size, x, y):
		font = pg.font.Font(self.font_name, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect()
		text_rect.midtop = (x, y)
		self.window.blit(text_surface, text_rect)
		
g = Game()

while g.running:
	g.run()

pg.quit()