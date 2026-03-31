"""
Script simple para entrenar modelos ML del bot
"""

import sys
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from ml_model import MLPredictor

def main():
    print("="*60)
    print("ENTRENAMIENTO DE MODELOS ML - Soccer Betting Bot")
    print("="*60)
    print()

    predictor = MLPredictor()

    print("Metodos de entrenamiento disponibles:")
    print("1. Simplificado (datos sinteticos) - Rapido, 2-3 minutos")
    print("2. Completo (datos reales FBref) - Lento, 15-30 minutos")
    print()
    print("Si falla opcion 2, se usara automaticamente opcion 1.")
    print()

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Elige metodo (1 o 2) [default: 1]: ").strip() or "1"

    print()
    print("-"*60)

    if choice == "1":
        print("Usando metodo simplificado con datos sinteticos...")
        print()
        success = predictor.train_model(use_simple=True)
    else:
        print("ADVERTENCIA: El metodo completo descarga datos historicos.")
        print("Puede tomar 15-30 minutos y requerir conexion a internet.")
        print()

        if len(sys.argv) > 2 and sys.argv[2] == '--yes':
            confirm = 's'
        else:
            confirm = input("Continuar? (s/n): ").strip().lower()

        if confirm == 's' or confirm == 'si':
            print()
            print("Iniciando entrenamiento completo...")
            print()
            success = predictor.train_model(use_simple=False)
        else:
            print()
            print("Cancelado. Usando metodo simplificado...")
            print()
            success = predictor.train_model(use_simple=True)

    print()
    print("="*60)

    if success:
        print("ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
        print("="*60)
        print()
        print("Los modelos estan listos para usar en el bot.")
        print()
        print("Prueba el bot con:")
        print("  python main.py")
        print()
        print("Y luego en Telegram:")
        print("  /fijini")
        print("  /partido Real Madrid vs Barcelona")
        print()

        # Test rapido
        print("-"*60)
        print("Test rapido de prediccion:")
        print()
        result = predictor.predict_match('Real Madrid', 'Barcelona', 'ESP')
        print(f"Real Madrid vs Barcelona:")
        print(f"  Victoria local: {result['ml_home_win_prob']}%")
        print(f"  Empate: {result['ml_draw_prob']}%")
        print(f"  Victoria visitante: {result['ml_away_win_prob']}%")
        print(f"  Confidence: {result['ml_confidence']}/100")
        print()
    else:
        print("ERROR EN ENTRENAMIENTO")
        print("="*60)
        print()
        print("Intenta el metodo simplificado:")
        print("  python train_ml.py 1")
        print()

if __name__ == '__main__':
    main()
