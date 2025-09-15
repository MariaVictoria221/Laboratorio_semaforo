from machine import Pin, mem32, ADC, TouchPad # type: ignore
from time import sleep_ms, sleep

# -------------------
# Pines de semáforo y peatonales
salida = [25,17,16,14,12,13,5,23,19,18,21,22,27,2,0,4]  # todos los LEDs de semáforo
GPIO = 0x03FF44004

for pin_num in salida:
    Pin(pin_num, Pin.OUT).off()  # todos apagados al inicio

# -------------------
# Potenciómetro para tiempos
potenciometro = ADC(36)
potenciometro.atten(ADC.ATTN_11DB)
potenciometro.width(ADC.WIDTH_12BIT)

def tiempo_pot():
    valor = potenciometro.read()
    print("Valor potenciómetro:", valor)
    return int(500 + (valor / 4095) * 2500)  # 500–3000 ms

# -------------------
# Pulsador peatonal
peatonal_solicitado = False
def activar_peatonal(pin):
    global peatonal_solicitado
    peatonal_solicitado = True
    print("Pulsador peatonal presionado")
pulsador_peatonal = Pin(32, Pin.IN, Pin.PULL_UP)
pulsador_peatonal.irq(trigger=Pin.IRQ_FALLING, handler=activar_peatonal)

# -------------------
# Modo cardiaco
modo = 0  # 0 semáforo, 1 cardiaco
led_cardiaco = Pin(4, Pin.OUT)   # LED en pin 4
buzzer = Pin(26, Pin.OUT)
touch = TouchPad(Pin(33))

def cambiar_modo(pin):
    global modo
    modo = not modo
    print("Modo cambiado:", "Semáforo" if modo == 0 else "Cardiaco")
    sleep(0.3)

pulsador_modo = Pin(15, Pin.IN, Pin.PULL_UP)
pulsador_modo.irq(trigger=Pin.IRQ_FALLING, handler=cambiar_modo)

# -------------------
# Función semáforo normal
def fase_semaforo(patron, duracion):
    mem32[GPIO] = patron
    sleep_ms(duracion)

def cruce_peatonal():
    global peatonal_solicitado
    print("Cruce peatonal activado")
    PATRON_PEATONAL = 0B0000000010100000000000000000
    mem32[GPIO] = PATRON_PEATONAL
    sleep_ms(tiempo_pot()*4)
    peatonal_solicitado = False

def modo_semaforo_normal():
    global peatonal_solicitado
    # --- Primer rojo fijo ---
    fase_semaforo(0B0000110000110001000000000001, 2150)
    fase_semaforo(0B0000100000010001000000000001, 200)
    fase_semaforo(0B0000110000110001000000000001, 2150)
    fase_semaforo(0B0000100000010001000000000001, 200)
    fase_semaforo(0B0000110000110001000000000001, 2150)
    fase_semaforo(0B0000101000110001000000000001, 2150)
    
    # --- Resto de fases ---
    fase_semaforo(0B0010100001000101000000000001, tiempo_pot())
    fase_semaforo(0B0010100001000101000000000000, tiempo_pot())
    fase_semaforo(0B0010100001000101000000000001, tiempo_pot())
    fase_semaforo(0B0010100001000101000000000000, tiempo_pot())
    fase_semaforo(0B0010100001000101000000000001, tiempo_pot())
    fase_semaforo(0B0010100001000101000000000100, tiempo_pot())
    fase_semaforo(0B0010000011000100000000110000, tiempo_pot())
    fase_semaforo(0B0010000001000000000000010000, tiempo_pot())
    fase_semaforo(0B0010000011000100000000110000, tiempo_pot())
    fase_semaforo(0B0010000001000000000000010000, tiempo_pot())
    fase_semaforo(0B0010000011000100000000110000, tiempo_pot())
    fase_semaforo(0B1010000011000010000000010000, tiempo_pot())

    # --- Cruce peatonal ---
    if peatonal_solicitado:
        cruce_peatonal()

# Modo cardiaco
# Funcionamiento modo cardiaco
def modo_cardiaco():
    valor = touch.read()
    if valor < 100:
        buzzer.on()
        led_cardiaco.on()
        mem32[GPIO] = 0B0100000000000000000000010000
    else:
        buzzer.off()
        led_cardiaco.off()
sleep(0.1)

# -------------------
# Bucle principal
while True:
    if modo == 0:
        modo_semaforo_normal()
    else:
        modo_cardiaco()
