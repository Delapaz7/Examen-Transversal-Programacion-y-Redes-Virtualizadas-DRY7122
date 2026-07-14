# Script que identifica si una VLAN pertenece al rango normal o extendido

try:
    vlan = int(input("Ingrese el número de VLAN: "))

    if 1 <= vlan <= 1005:
        print(f"La VLAN {vlan} pertenece al rango normal.")

    elif 1006 <= vlan <= 4094:
        print(f"La VLAN {vlan} pertenece al rango extendido.")

    else:
        print("Número de VLAN inválido. Debe ingresar un número entre 1 y 4094.")

except ValueError:
    print("Error: debe ingresar solamente un número entero.")