import pygame
import math

# --- CONSTANTES FÍSICAS (MARTE) ---
GRAVITY_MARS = 3.71
ATM_DENSITY_MARS = 0.020
ISP = 300
G0 = 9.80665

class PIDController:
    """Controlador industrial con Anti-Windup y Derivada Filtrada."""
    def __init__(self, kp, ki, kd, setpoint=0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.setpoint = setpoint
        self.integral = 0
        self.prev_error = 0

    def compute(self, current_val, dt):
        error = self.setpoint - current_val
        # Anti-Windup: Evita que la integral crezca infinitamente si el motor satura
        self.integral = max(-100, min(self.integral + error * dt, 100))
        
        derivative = (error - self.prev_error) / dt
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.prev_error = error
        return output

class RocketSimulation:
    def __init__(self, altitude, velocity, dry_mass, fuel_mass):
        self.y = altitude
        self.v = velocity
        self.m_dry = dry_mass
        self.m_fuel = fuel_mass
        self.thrust = 0
        self.max_thrust = 15000.0
        self.area = 10.0
        self.cd = 0.5

    def update_physics(self, u_cmd, dt):
        """Implementación de Semi-Implicit Euler."""
        if self.y <= 0:
            return False # Ground contact

        # 1. Gestión de Masa y Empuje
        self.thrust = max(0, min(u_cmd, self.max_thrust))
        if self.m_fuel <= 0:
            self.thrust = 0
            
        total_mass = self.m_dry + self.m_fuel
        # Consumo de combustible basado en la ecuación del cohete
        fuel_burn = (self.thrust / (ISP * G0)) * dt
        self.m_fuel = max(0, self.m_fuel - fuel_burn)

        # 2. Cálculo de Fuerzas
        drag = -0.5 * ATM_DENSITY_MARS * self.v * abs(self.v) * self.cd * self.area
        gravity_force = -total_mass * GRAVITY_MARS
        net_force = gravity_force + drag + self.thrust
        acceleration = net_force / total_mass

        # 3. SEMI-IMPLICIT EULER (V antes que Y)
        self.v += acceleration * dt
        self.y += self.v * dt

        if self.y < 0:
            self.y = 0
            self.v = 0
        return True

def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 700))
    clock = pygame.time.Clock()
    
    # Inicialización basada en tu perfil de Ingeniería Aeroespacial [cite: 5]
    rocket = RocketSimulation(altitude=1000.0, velocity=-10.0, dry_mass=500.0, fuel_mass=600.0)
    # Control de velocidad para aterrizaje suave (Vertical Landing)
    controller = PIDController(kp=1200, ki=20, kd=800, setpoint=-2.0)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if dt > 0.1: dt = 0.1

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        # Lógica de Control: Compensación de Gravedad + Salida PID
        current_weight = (rocket.m_dry + rocket.m_fuel) * GRAVITY_MARS
        thrust_cmd = controller.compute(rocket.v, dt) + current_weight

        rocket.update_physics(thrust_cmd, dt)

        # Rendering Minimalista (Estilo Dashboard de Telemetría)
        screen.fill((10, 10, 15))
        # Dibujar Marte
        pygame.draw.rect(screen, (135, 62, 35), (0, 650, 400, 50))
        # Dibujar Cohete (Escalado simple)
        rocket_py = 650 - (rocket.y * 0.6)
        pygame.draw.rect(screen, (200, 200, 200), (190, rocket_py, 20, 40))
        
        # Telemetría en consola (Cero Complacencia: Monitorea tus estados)
        if int(rocket.y) % 10 == 0:
            print(f"Alt: {rocket.y:.1f}m | Vel: {rocket.v:.1f}m/s | Fuel: {rocket.m_fuel:.1f}kg")

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()