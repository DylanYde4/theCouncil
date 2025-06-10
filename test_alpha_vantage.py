"""
Script para probar la conexión con Alpha Vantage directamente.
"""
import os
import sys
import asyncio
import json
from dotenv import load_dotenv
import httpx

# Cargar variables de entorno
load_dotenv()

async def test_alpha_vantage():
    """Prueba la conexión con Alpha Vantage usando una API key."""
    # Obtener API key
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    print(f"Usando API key: {api_key[:4]}{'*' * (len(api_key) - 4) if len(api_key) > 4 else '*'}")
    
    # URL de la API
    base_url = "https://www.alphavantage.co/query"
    
    # Parámetros de la solicitud
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": "GPRK",
        "apikey": api_key
    }
    
    try:
        print(f"Enviando solicitud a {base_url} para obtener información de GPRK...")
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            print("\nRespuesta de Alpha Vantage:")
            print(json.dumps(data, indent=2))
            
            if "Global Quote" in data:
                print("\n✅ Conexión exitosa! Se recibieron datos válidos.")
                price = data["Global Quote"].get("05. price", "N/A")
                print(f"Precio actual de GPRK: {price}")
            elif "Error Message" in data:
                print(f"\n❌ Error en la API: {data['Error Message']}")
            elif "Note" in data and "call frequency" in data["Note"]:
                print(f"\n⚠️ Límite de frecuencia excedido: {data['Note']}")
            else:
                print("\n❓ Respuesta inesperada. Verifica los detalles anteriores.")
                
    except httpx.HTTPStatusError as e:
        print(f"\n❌ Error HTTP: {e.response.status_code} - {e.response.reason_phrase}")
        if e.response.text:
            print(f"Detalles: {e.response.text}")
    except httpx.RequestError as e:
        print(f"\n❌ Error de conexión: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    print("=== Test de conexión con Alpha Vantage ===")
    asyncio.run(test_alpha_vantage())
    print("\n=== Fin del test ===") 