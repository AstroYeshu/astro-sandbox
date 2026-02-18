import pygame
import math

# --- CONSTANTES FÍSICAS Y DEL SIMULADOR ---
# Usamos "Unidades de Simulación" manejables, no metros reales, para que encaje en pantalla.
MU = 1000000      # Parámetro Gravitacional (G * M)
R_INNER = 100     # Radio de la órbita inicial (px)
R_OUTER = 300     # Radio de la órbita final (px)

WIDTH, HEIGHT = 800, 600
CENTER = (WIDTH // 2, HEIGHT // 2)

class Spacecraft:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.orbit_path = [] # Para dibujar la estela

    def update(self, dt):
        # 1. Calcular el vector de posición relativa al planeta
        rx = self.x - CENTER[0]
        ry = self.y - CENTER[1]
        r_mag_sq = rx**2 + ry**2
        r_mag = math.sqrt(r_mag_sq)

        # 2. Calcular Aceleración (Gravedad) a = - (mu / r^3) * r_vec
        # La intuición: La fuerza disminuye con el cuadrado de la distancia, 
        # y multiplicamos por el vector unitario (rx/r_mag) para dar dirección.
        acc_mag = -MU / (r_mag_sq * r_mag)
        ax = acc_mag * rx
        ay = acc_mag * ry

        # 3. Integración de Euler Semi-implícita (Velocidad PRIMERO)
        self.vx += ax * dt
        self.vy += ay * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Guardar estela
        self.orbit_path.append((self.x, self.y))
        if len(self.orbit_path) > 300:
            self.orbit_path.pop(0)

    def apply_prograde_impulse(self, delta_v):
        # Aceleramos en la dirección exacta en la que nos movemos.
        v_mag = math.sqrt(self.vx**2 + self.vy**2)
        dir_x = self.vx / v_mag
        dir_y = self.vy / v_mag
        
        self.vx += dir_x * delta_v
        self.vy += dir_y * delta_v

def calculate_hohmann_deltas():
    # Velocidades circulares
    v_inner_circ = math.sqrt(MU / R_INNER)
    v_outer_circ = math.sqrt(MU / R_OUTER)

    # Semieje mayor de la órbita de transferencia elíptica
    a_transfer = (R_INNER + R_OUTER) / 2

    # Vis-viva para el perigeo de la transferencia (punto más bajo)
    v_transfer_periapsis = math.sqrt(MU * (2 / R_INNER - 1 / a_transfer))
    
    # Vis-viva para el apogeo de la transferencia (punto más alto)
    v_transfer_apoapsis = math.sqrt(MU * (2 / R_OUTER - 1 / a_transfer))

    # Los Deltas son la diferencia entre la velocidad que TENDREMOS y la que TENEMOS
    dv1 = v_transfer_periapsis - v_inner_circ
    dv2 = v_outer_circ - v_transfer_apoapsis

    return dv1, dv2

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulador Riguroso: Transferencia de Hohmann")
    clock = pygame.time.Clock()

    # Cálculo analítico de los requerimientos de misión
    dv1, dv2 = calculate_hohmann_deltas()
    print(f"Δv1 Requerido (Escape a Transferencia): {dv1:.2f}")
    print(f"Δv2 Requerido (Circularización): {dv2:.2f}")

    # Inicialización de la nave en órbita circular interna
    # Empezamos en x = CENTER + R_INNER, y = CENTER. 
    # Para orbitar, la velocidad debe ser puramente en Y.
    v_initial = math.sqrt(MU / R_INNER)
    ship = Spacecraft(CENTER[0] + R_INNER, CENTER[1], 0, v_initial)

    running = True
    stage = 0 # 0: Interna, 1: Transferencia, 2: Externa

    while running:
        dt = clock.tick(60) / 1000.0 # Delta time en segundos
        # Aceleramos la simulación artificialmente para no esperar tanto
        sim_speed = 5 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and stage == 0:
                    print("Ejecutando Impulso 1: Inyección de Transferencia")
                    ship.apply_prograde_impulse(dv1)
                    stage = 1
                elif event.key == pygame.K_2 and stage == 1:
                    print("Ejecutando Impulso 2: Circularización")
                    ship.apply_prograde_impulse(dv2)
                    stage = 2

        # Física
        for _ in range(sim_speed):
            ship.update(dt)

        # Renderizado
        screen.fill((10, 10, 20)) # Espacio profundo
        
        # Planeta masivo central
        pygame.draw.circle(screen, (100, 200, 255), CENTER, 20)
        
        # Órbitas de referencia (Visuales)
        pygame.draw.circle(screen, (50, 50, 50), CENTER, R_INNER, 1)
        pygame.draw.circle(screen, (50, 50, 50), CENTER, R_OUTER, 1)

        # Estela de la nave
        if len(ship.orbit_path) > 1:
            pygame.draw.lines(screen, (255, 100, 100), False, ship.orbit_path, 2)

        # Nave
        pygame.draw.circle(screen, (255, 255, 255), (int(ship.x), int(ship.y)), 5)

        # UI Text
        font = pygame.font.SysFont(None, 24)
        info1 = font.render("Presiona '1' en el punto inferior para Inyección (Δv1)", True, (255,255,255))
        info2 = font.render("Presiona '2' al llegar al punto superior para Circularizar (Δv2)", True, (255,255,255))
        screen.blit(info1, (10, 10))
        screen.blit(info2, (10, 30))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()