# -*- coding: utf-8 -*-
from app.chat_engine import ChatEngine
from app.model_loader import check_system_resources, is_port_in_use, verify_ollama_connection

def main():
    """Funcion principal para probar el chat"""
    # Verificar recursos y conexion
    check_system_resources()
    print("\n=== Chat con Ollama ===")
    # Verificar estado de Ollama
    port_used, port_msg = is_port_in_use()
    print("Estado del puerto: ", port_msg, "\npuerto usado: ",port_used)
    if not port_used:
        print("[Error]: Ollama no esta ejecutandose")
        return
    ok, msg = verify_ollama_connection()
    print("Estado de conexion:", ok, "\nseguimos dentro de main.py")
    if not ok:
        print("\033[91mALERTA ALERTA\033[0m")
        print("[Error]: No se pudo conectar a Ollama:", msg)
        print("Asegurate de que Ollama esta ejecutandose")
        print("Ejecuta: ollama serve --model tinyllama:latest")
        return
    # Verificar modelo disponible
    ok = ChatEngine.verificar_modelo("llama2")
    msg = "Sin mensaje, la funcion no lo proporciona"    
    print("Estado de conexion:", msg, "\nseguimos dentro de main.py")
    print("Estado de modelo:", ok)
    # Si no hay conexion o modelo, salir    
    if not ok:
        return
    # Iniciar chat
    chat = ChatEngine(model="llama2")
    if not chat.check_connection():
        print("[Error]: No se pudo establecer conexion con el modelo")
        return
    # Instrucciones
    print("\nChat iniciado!")
    print("Comandos disponibles:")
    print("- 'salir', 'exit', 'quit': Terminar chat")
    print("- 'reiniciar', 'reset': Reiniciar conversacion")
    print("- 'history': Mostrar historial")
    print("- 'clear': Limpiar pantalla")
    # Bucle principal del chat
    while True:
        try:
            user_input = input("\nTu > ").strip()    
            # Procesar comandos especiales
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("Hasta luego!")
                break


                


            if user_input.lower() in ['reiniciar', 'reset']:


                chat.reset()


                print("Conversacion reiniciada")


                continue


                


            if user_input.lower() == 'history':


                history = chat.get_conversation_history()


                print("\n=== Historial ===")


                for msg in history:


                    role = "Tu" if msg["role"] == "user" else "Asistente"


                    print(f"{role} > {msg['content']}")


                continue


                


            if user_input.lower() == 'clear':


                import os


                os.system('cls' if os.name == 'nt' else 'clear')


                continue


                


            if not user_input:  # Ignorar entradas vacias


                continue


            


            # Procesar pregunta normal


            print("Procesando...", end="\r")


            response = chat.ask(user_input)


print("[chat_test.py][main] " * 20, end="\r")  # Limpiar "Procesando..."


            


            if isinstance(response, str):


                print("\nAsistente >", response)


            else:


                print("\nAsistente >", response.get('response', '[Error: Respuesta vacia]'))


            


        except KeyboardInterrupt:


            print("\n\nHasta luego!")


            break


        except Exception as e:


            print("\n[Error]:", str(e))


            print("Reiniciando conversacion...")


            chat.reset()





if __name__ == "__main__":


    main()