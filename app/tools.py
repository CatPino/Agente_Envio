import datetime
import os

def guardar_registro_log(args):
    texto = args.get("texto")
    ahora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ruta = "/workspaces/Agente_Envio/log_operaciones.txt"
    
    print(f"DEBUG - Intentando escribir en: {ruta}")
    print(f"DEBUG - Texto: {texto}")
    
    try:
        with open(ruta, "a") as f:
            f.write(f"\n[{ahora}] - {texto}")
        print("DEBUG - Escritura exitosa")
        return "Registro guardado correctamente en el archivo log_operaciones.txt."
    except Exception as e:
        print(f"DEBUG - Error: {str(e)}")
        return f"Error al escribir el log: {str(e)}"