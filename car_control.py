import pygame
import math

pygame.init()

GAMEW , GAMEH = 800,600
PANELH = 120
W , H  = GAMEW,GAMEH
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Car Control")
FONT = pygame.font.SysFont("comicsans", 22)

# colors
GAME_BG = (18,18,18)
PANEL_BG = (40,40,40)
CAR_COLOR = (255, 255, 0)
OBSTACLE_COLOR = (255,60,60)
SENSOR_COLOR = (200,200,200)
TEXT_COLOR = (220,220,220)

# CAR PHYSICS
CAR_W,CAR_H = 45,30
MAX_SPEED = 250
MAX_ACCEL = 600
BRAKE_FORCE = 4.0
FRICTION = 220
MAX_STEER_RATE = math.radians(160)
STEER_SMOOTHING = 8.0

# sensors
MAX_SENSOR_DIST = 200
SENSOR_ANGLE = [-math.pi/3,-math.pi/6,0,math.pi/3,math.pi/6]
SENSOR_STEP = 5

# HELPER FUNCTIONS
def point_to_segment_distance(px,py,ax,ay,bx,by):
    vx,vy = px - ax, py - ay
    ux,uy = bx - ax, by - ay
    seg = ux**2 + uy**2

    if seg == 0 :
        return math.hypot(vx,vy)

    t = max(0,min(1,(vx*ux + vy*uy)/seg))
    projx = ax + t * ux
    projy = ay + t * uy
    return math.hypot(px - projx,py - projy)

def ray_cast(origin,angle,obstacles):
    ox , oy = origin
    dx , dy = math.cos(angle), math.sin(angle)
    for d in range(0, MAX_SENSOR_DIST,SENSOR_STEP):
        px = ox + dx * d
        py = oy + dy * d

        if px < 0 or px> GAMEW or py < 0 or py > GAMEH:
            return d

        for i in range (0,len(obstacles)-1,2):
            if(point_to_segment_distance(px,py,obstacles[i][0],obstacles[i][1],
                                         obstacles[i+1][0],obstacles[i+1][1]) < 2):
                return d
    return MAX_SENSOR_DIST  # ray didn't hit

class Car:
    def __init__(self):
        self.x = CAR_W
        self.y = CAR_H
        self.speed = 0
        self.angle = 0
        self.angular_velocity = 0

    def step(self,dt,throttle,brake,steer):
        accl = throttle * MAX_ACCEL
        deaccl = brake * MAX_ACCEL * BRAKE_FORCE

        self.speed += (accl - deaccl) * dt

        if throttle < 0.1 :
            self.speed -= FRICTION * dt

        self.speed = max(0,min(self.speed,MAX_SPEED))

        # simulalting rotational motion
        target_av = steer * MAX_STEER_RATE
        self.angular_velocity += (target_av - self.angular_velocity) * min(1.0,STEER_SMOOTHING * dt)
        self.angle += self.angular_velocity * dt

        prev_x,prev_y = self.x,self.y
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt

        dist = math.hypot(self.x - prev_x,self.y-prev_y)
        return dist


    def draw(self,surface):
        car_s = pygame.Surface((CAR_W,CAR_H))
        pygame.draw.rect(car_s, CAR_COLOR, (0, 0, CAR_W, CAR_H), border_radius=5)
        rot = pygame.transform.rotate(car_s, -math.degrees(self.angle))
        surface.blit(rot, (rot.get_rect(center = (self.x,self.y))))


def main():
    car = Car()
    clock = pygame.time.Clock()
    running = True
    score = 0
    max_score = 0
    game_over = False

    obstacles = []
    prev_mouse = None

    show_sensor = True

    while running:
        dt = clock.tick(60)/1000
        screen.fill(GAME_BG)
        pygame.draw.rect(screen,PANEL_BG,(0,H,W,PANELH))

        #EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    show_sensor = not show_sensor
                elif event.key == pygame.K_c:
                    obstacles.clear()

        # user input
        keys = pygame.key.get_pressed()
        throttle = 0
        brake = 0
        steer = 0

        if keys[pygame.K_UP] or  keys[pygame.K_w]:
            throttle = 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            brake = 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            steer = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            steer = 1

        # draw
        if pygame.mouse.get_pressed()[0] and not game_over:
            mx,my = pygame.mouse.get_pos()
            if my < GAMEH - PANELH :
                if prev_mouse :
                    obstacles.extend([prev_mouse,(mx,my)])
                prev_mouse = mx,my
        else :
            prev_mouse = None

        # updates
        if not game_over:
            dist = car.step(dt,throttle,brake,steer)

            if dist < 1.0:
                score += 1
                max_score = max(max_score,score)

        # Draw obstacles
        for i in range(0,len(obstacles)-1,2):
            pygame.draw.line(screen,OBSTACLE_COLOR,obstacles[i],obstacles[i+1],3)

        # Draw Sensor
        if show_sensor and not game_over:
            for a in SENSOR_ANGLE:
                d = ray_cast((car.x,car.y),car.angle+a,obstacles)
                end_x = car.x + math.cos(car.angle + a)*d
                end_y = car.y + math.sin(car.angle + a)*d
                pygame.draw.line(screen,SENSOR_COLOR,
                                 (car.x,car.y),
                                 (end_x,end_y),1
                                 )
                pygame.draw.circle(screen,SENSOR_COLOR,
                                   (int(end_x),int(end_y)),
                                   3
                                   )

        car.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()