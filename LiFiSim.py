# Light simulation, Roemen, Chris, Cot
import pygame
import math
import sys

pygame.init()
W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("LiFi Laser Simulation")
clock = pygame.time.Clock()

# Colors
BLACK = (0,0,0)
BLUE  = (80,180,255)
GREEN = (60,220,60)
CYAN  = (0,255,255)
RED   = (255,60,60)
YELLOW = (255,220,60)
LIGHT_GRAY = (220,220,220)

# Fonts
FONT = pygame.font.SysFont(None, 32)
BIG  = pygame.font.SysFont(None, 48)
SMALL = pygame.font.SysFont(None, 20)

# Beam length, lazers are supposed to be long and focused so 100 seemed correct
BEAM_LEN = 1000

# Input bits
input_bits = ""
MAX_BITS = 8

# Draws text on screen
def draw_text(text, font, color, x, y):
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))
    return surf.get_rect(topleft=(x, y))
# self explanitory 
def draw_grid(spacing=50):
    for x in range(0, W, spacing):
        pygame.draw.line(screen, LIGHT_GRAY, (x,0),(x,H),1)
    for y in range(0, H, spacing):
        pygame.draw.line(screen, LIGHT_GRAY, (0,y),(W,y),1)

# these two functions make the beams look good
def get_beam_end(pos, angle_deg, length=BEAM_LEN):
    rad = math.radians(angle_deg)
    return pygame.Vector2(pos.x + math.cos(rad)*length,
                          pos.y + math.sin(rad)*length)

def get_beam_towards(pos, target_pos, max_length=BEAM_LEN):
    """Returns a point along the line from pos to target_pos, limited by max_length."""
    direction = target_pos - pos
    if direction.length() > max_length:
        direction.scale_to_length(max_length)
    return pos + direction

# initial starting point
class Transmitter:
    def __init__(self, x, y, w=80, h=60):
        self.pos = pygame.Vector2(x, y)
        self.angle = 0.0
        self.locked = False
        self.impact_angle = None
        self.impact_point = get_beam_end(self.pos, self.angle)
        self.size = (w,h)

    def update(self, splitter):
        if not self.locked:
            # Beam toward splitter center
            end = get_beam_towards(self.pos, splitter.pos)
            if splitter.rect.collidepoint(end):
                self.locked = True
                self.impact_angle = math.degrees(math.atan2(end.y - self.pos.y, end.x - self.pos.x))
                self.impact_point = splitter.pos  # stop at center
            else:
                self.angle = (self.angle + 1.0) % 360
                self.impact_point = get_beam_end(self.pos, self.angle)
        else:
            self.impact_point = splitter.pos

    def draw(self, surf):
        pygame.draw.rect(surf, BLUE, (self.pos.x - self.size[0]/2, self.pos.y - self.size[1]/2,
                                      self.size[0], self.size[1]))
        draw_text("Transmitter", FONT, BLACK, self.pos.x - self.size[0]/2 + 5,
                  self.pos.y - self.size[1]/2 + 5)
        pygame.draw.line(surf, GREEN if self.locked else CYAN, self.pos, self.impact_point, 3)

# Beam Class ( Simulates how system would actually work in real life aka it would lock on or scan the
# area and stuff)
class BeamSplitter:
    def __init__(self, x, y, radius=30):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius
        self.angle = 0.0
        self.locked_on_rx = False
        self.impact_point = self.pos

    @property
    def rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius,
                           self.radius*2, self.radius*2)

    def update(self, transmitter, receiver):
        if not transmitter.locked:
            return

        start = self.pos
        receiver_center = pygame.Vector2(receiver.rect.center)
        incoming = transmitter.impact_angle

        # If not currently locked or receiver moved out, rotate
        if not self.locked_on_rx or not receiver.rect.collidepoint(self.impact_point):
            self.angle = (self.angle + 5.0) % 360  # scanning rotation
            outgoing_angle = (2 * self.angle - incoming) % 360
            end = get_beam_end(start, outgoing_angle, BEAM_LEN)

            # Check if beam intersects receiver
            clipped_line = receiver.rect.clipline(int(start.x), int(start.y), int(end.x), int(end.y))
            if clipped_line:
                self.impact_point = pygame.Vector2(clipped_line[0])
                self.locked_on_rx = True
            else:
                self.impact_point = end
                self.locked_on_rx = False
        else:
            # Keep tracking receiver if locked
            clipped_line = receiver.rect.clipline(int(start.x), int(start.y),
                                                int(receiver_center.x), int(receiver_center.y))
            if clipped_line:
                self.impact_point = pygame.Vector2(clipped_line[0])
            else:
                self.locked_on_rx = False  # lost lock if receiver moved away 

        # Draw the beam
        pygame.draw.line(screen, GREEN if self.locked_on_rx else CYAN, start, self.impact_point, 3)




    def draw(self, surf):
        pygame.draw.circle(surf, BLUE, (int(self.pos.x), int(self.pos.y)), self.radius)
        draw_text("Beam Splitter", FONT, BLACK, self.pos.x - self.radius + 5, self.pos.y - self.radius + 5)

# Receiver class
class Receiver:
    def __init__(self, x, y, w=120, h=70):
        self.rect = pygame.Rect(x, y, w, h)
        self.display_offset = pygame.Vector2(w+20, 10)

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(0, min(W - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(H - self.rect.height, self.rect.y))


    def draw(self, surf, output_bits=""):
        pygame.draw.rect(surf, BLUE, self.rect)
        draw_text("Receiver", FONT, BLACK, self.rect.x + 10, self.rect.y + 10)
        display_pos = pygame.Vector2(self.rect.topleft) + self.display_offset
        pygame.draw.rect(surf, BLUE, (display_pos.x, display_pos.y, 160, 60))
        draw_text("Display", FONT, BLACK, display_pos.x + 10, display_pos.y + 5)
        if output_bits:
            draw_text(output_bits, BIG, YELLOW, display_pos.x + 10, display_pos.y + 25)

# Objects, transmitter, receiver, beamsplitter
tx = Transmitter(W*0.25, H*0.8)
splitter = BeamSplitter(W*0.35, H*0.5)
rx = Receiver(W*0.70, H*0.3)
rx2 = Receiver(W*0.5 - 60, H*0.85)  # bottom center receiver


running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            if e.unicode in ("0","1") and len(input_bits)<MAX_BITS:
                input_bits += e.unicode
            if e.key == pygame.K_BACKSPACE:
                input_bits = input_bits[:-1]

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        rx.move(-5, 0)
    if keys[pygame.K_RIGHT]:
        rx.move(5, 0)
    if keys[pygame.K_UP]:
        rx.move(0, -5)
    if keys[pygame.K_DOWN]:
        rx.move(0, 5)


    screen.fill((240,245,255))
    draw_grid(50)

    # Update logic
    tx.update(splitter)
    splitter.update(tx, rx)

    # Direct TX -> RX2 beam
    tx_to_rx2_end = get_beam_towards(tx.pos, pygame.Vector2(rx2.rect.center))
    direct_rx2_hit = rx2.rect.collidepoint(tx_to_rx2_end)

    # Draw everything
    tx.draw(screen)
    splitter.draw(screen)
    pygame.draw.line(screen, GREEN if direct_rx2_hit else CYAN, tx.pos, tx_to_rx2_end, 3)
    rx.draw(screen, output_bits=input_bits if splitter.locked_on_rx and len(input_bits)==MAX_BITS else "")
    rx2.draw(screen, output_bits=input_bits if direct_rx2_hit and len(input_bits)==MAX_BITS else "")

    # Input box
    pygame.draw.rect(screen, BLACK, (25,25,350,50),2)
    draw_text(f"Input (8 bits): {input_bits}", FONT, BLACK, 30, 30)

    # Status panel
    display_pos = pygame.Vector2(rx.rect.topleft) + rx.display_offset
    draw_text(f"TX Position: ({int(tx.pos.x)},{int(tx.pos.y)})", SMALL, BLACK, 30, 90)
    draw_text(f"Splitter: ({int(splitter.pos.x)},{int(splitter.pos.y)})", SMALL, BLACK, 30, 115)
    draw_text(f"RX Position: ({int(rx.rect.x)},{int(rx.rect.y)})", SMALL, BLACK, 30, 140)
    draw_text(f"Display: ({int(display_pos.x)},{int(display_pos.y)})", SMALL, BLACK, 30, 165)

    # Top-right status
    status_splitter = "FOUND" if tx.locked else "SEARCHING"
    color_splitter = GREEN if tx.locked else RED
    draw_text("Splitter: ", FONT, BLACK, W - 330, 30)
    draw_text(status_splitter, FONT, color_splitter, W - 200, 30)

    status_receiver = "FOUND" if splitter.locked_on_rx else "SEARCHING"
    color_receiver = GREEN if splitter.locked_on_rx else RED
    draw_text("Beam-Receiver: ", FONT, BLACK, W - 330, 70)
    draw_text(status_receiver, FONT, color_receiver, W - 150, 70)

    status_rx2 = "FOUND" if direct_rx2_hit else "SEARCHING"
    color_rx2 = GREEN if direct_rx2_hit else RED
    draw_text("Direct-RX2: ", FONT, BLACK, W - 330, 110)
    draw_text(status_rx2, FONT, color_rx2, W - 180, 110)

    draw_text("Controls: LEFT/RIGHT Arrow Keys to move receiver/display", FONT, BLACK, 30, H-40)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
