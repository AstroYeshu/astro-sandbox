import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN FÍSICA ---
GRAVEDAD_MARTE = 3.71  # m/s^2
DENSIDAD_ATM_MARTE = 0.020  # kg/m^3

class Cohete:
    def __init__(self, y_inicial, v_inicial, masa):
        # Estado del sistema (State Space)
        self.y = y_inicial  # Altura (m)
        self.v = v_inicial  # Velocidad (m/s)
        self.m = masa       # Masa (kg)
        
        # Parámetros fijos (Falcon 9 aprox)
        self.Cd = 0.5       # Coeficiente de arrastre
        self.Area = 10.0    # Área transversal (m^2)
        self.max_thrust = 15000.0  # Empuje máximo (N)

    def calcular_aceleracion(self, thrust_input):
        # 1. Fuerza de Gravedad (Peso)
        f_gravedad = -self.m * GRAVEDAD_MARTE
        
        # 2. Fuerza de Arrastre (Drag)
        # Recordatorio: v * abs(v) asegura que el arrastre siempre se oponga al movimiento
        f_arrastre = -0.5 * DENSIDAD_ATM_MARTE * self.v * abs(self.v) * self.Cd * self.Area
        
        # 3. Empuje (Thrust) con saturación (0% a 100%)
        u = max(0, min(thrust_input, self.max_thrust))
        
        # F = ma -> a = F/m
        f_neta = f_gravedad + f_arrastre + u
        return f_neta / self.m

    def step(self, u_cmd, dt):
        """Integrador Euler Semi-Implícito"""
        a = self.calcular_aceleracion(u_cmd)
        
        # Actualizamos velocidad primero, luego posición
        self.v += a * dt
        self.y += self.v * dt
        
        # Condición de suelo
        if self.y <= 0:
            self.y = 0
            self.v = 0
            return False # Contacto con el suelo
        return True # Sigue en vuelo

# --- MAIN LOOP (Simulación) ---

def simular():
    # Inicialización: 1000m de altura, quieto, 500kg
    falcon = Cohete(y_inicial=1000.0, v_inicial=0.0, masa=500.0)
    dt = 0.1
    t_max = 50.0
    
    # Listas para telemetría
    hist_t, hist_y, hist_v, hist_u = [], [], [], []
    
    t = 0
    print("Iniciando descenso en Marte...")
    
    while t < t_max:
        # --- LÓGICA DE CONTROL (AQUÍ VA TU MAGIA) ---
        # Por ahora, un control simple: encender al 100% si estamos a menos de 200m
        if falcon.y < 200:
            u = falcon.max_thrust
        else:
            u = 0.0
        # --------------------------------------------
        
        hist_t.append(t)
        hist_y.append(falcon.y)
        hist_v.append(falcon.v)
        hist_u.append(u)
        
        en_vuelo = falcon.step(u, dt)
        
        if not en_vuelo:
            print(f"¡Contacto! T: {t:.1f}s | Vel de Impacto: {hist_v[-1]:.2f} m/s")
            break
        t += dt

    # Gráficas
    plt.figure(figsize=(10, 6))
    plt.subplot(3, 1, 1)
    plt.plot(hist_t, hist_y, label='Altura (m)')
    plt.grid(True); plt.legend()
    
    plt.subplot(3, 1, 2)
    plt.plot(hist_t, hist_v, color='red', label='Velocidad (m/s)')
    plt.grid(True); plt.legend()
    
    plt.subplot(3, 1, 3)
    plt.step(hist_t, hist_u, color='green', label='Empuje (N)')
    plt.show()

if __name__ == "__main__":
    simular()