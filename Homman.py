import pygame
import math

# --- CONFIGURACIÓN TÉCNICA (Primeros Principios) ---
MU = 1000000      # Parámetro gravitacional
R_INNER = 100     # Órbita de estacionamiento (px)
R_OUTER = 300     # Órbita objetivo (px)
WIDTH, HEIGHT = 800, 600
CENTER = pygame.Vector2(WIDTH // 2, HEIGHT // 2)

class OrbitalState:
    """Manejo de Vectores de Estado para Mecánica Orbital."""
    def __init__(self, pos, vel):
        self.r = pygame.Vector2(pos)
        self.v = pygame.Vector2(vel)

class MissionSequencer:
    """Sistema de Guiado Robusto (GNC)."""
    def __init__(self):
        self.dv1, self.dv2 = self._calculate_deltas()
        self.stage = "PARKED"
        self.last_r_mag = R_INNER

    def _calculate_deltas(self):
        v_inner = math.sqrt(MU / R_INNER)
        v_outer = math.sqrt(MU / R_OUTER)
        a_trans = (R_INNER + R_OUTER) / 2
        v_peri = math.sqrt(MU * (2 / R_INNER - 1 / a_trans))
        v_apo = math.sqrt(MU * (2 / R_OUTER - 1 / a_trans))
        return (v_peri - v_inner), (v_outer - v_apo)

    def update(self, ship):
        r_mag = ship.state.r.length()
        
        # Maniobra 1: Inyección (Periapsis)
        # Si estamos estacionados y detectamos que estamos cerca del radio inicial
        if self.stage == "PARKED":
            ship.apply_impulse(self.dv1)
            self.stage = "TRANSFERRING"
            print(f"EVENT: TMI Executed at r={r_mag:.2f}")

        # Maniobra 2: Circularización (Apogeo)
        # Lógica: Si estamos transfiriendo y la distancia EMPIEZA A BAJAR, 
        # significa que acabamos de pasar el Apogeo.
        elif self.stage == "TRANSFERRING":
            # Detectamos que cruzamos el eje (x < 0) y que r_mag ya no crece
            if ship.state.r.x < 0 and r_mag < self.last_r_mag:
                ship.apply_impulse(self.dv2)
                self.stage = "TARGET_ORBIT"
                print(f"EVENT: Circularization at r={r_mag:.2f}")

        self.last_r_mag = r_mag

class SpacecraftPro:
    def __init__(self):
        # Iniciar en órbita circular interna
        v_init = math.sqrt(MU / R_INNER)
        self.state = OrbitalState((R_INNER, 0), (0, v_init))
        self.path = []

    def apply_impulse(self, dv_mag):
        if self.state.v.length() > 0:
            unit_v = self.state.v.normalize()
            self.state.v += unit_v * dv_mag

    def step(self, dt):
        # Física: Aceleración gravitacional a = - (mu / r^3) * r
        r_mag = self.state.r.length()
        accel = -MU / (r_mag**3) * self.state.r
        
        # Integración Semi-implícita de Euler
        self.state.v += accel * dt
        self.state.r += self.state.v * dt
        
        # Guardar estela para visualización
        self.path.append((int(self.state.r.x + CENTER.x), int(self.state.r.y + CENTER.y)))
        if len(self.path) > 1000: self.path.pop(0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Oracle Tech Demo: Automated Hohmann Transfer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Consolas", 16)

    ship = SpacecraftPro()
    sequencer = MissionSequencer()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        sim_dt = dt * 10 # Aceleración de tiempo para la simulación

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Lógica ---
        ship.step(sim_dt)
        sequencer.update(ship)

        # --- Renderizado ---
        screen.fill((5, 5, 15)) # Negro espacio
        
        # Dibujar Orbits de Referencia
        pygame.draw.circle(screen, (30, 30, 50), CENTER, R_INNER, 1)
        pygame.draw.circle(screen, (30, 30, 50), CENTER, R_OUTER, 1)
        
        # Planeta Central
        pygame.draw.circle(screen, (100, 150, 255), CENTER, 15)
        
        # Estela y Nave
        if len(ship.path) > 2:
            pygame.draw.lines(screen, (255, 100, 0), False, ship.path, 1)
        
        ship_pos = (int(ship.state.r.x + CENTER.x), int(ship.state.r.y + CENTER.y))
        pygame.draw.circle(screen, (255, 255, 255), ship_pos, 4)

        # UI / Telemetría
        ui_color = (0, 255, 150)
        telemetry = [
            f"Stage: {sequencer.stage}",
            f"Altitude: {ship.state.r.length():.2f} px",
            f"Velocity: {ship.state.v.length():.2f} px/s",
            f"Target: R={R_OUTER}"
        ]
        for i, text in enumerate(telemetry):
            surf = font.render(text, True, ui_color)
            screen.blit(surf, (10, 10 + i * 20))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()