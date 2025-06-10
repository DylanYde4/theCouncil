"""
Cliente para la API Alpha Vantage que obtiene datos financieros.
"""
import logging
import os
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)

class AlphaVantageClient:
    """Cliente para interactuar con la API Alpha Vantage."""
    
    # URL base de la API
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self):
        """Inicializa el cliente de Alpha Vantage."""
        # Obtener API key de las variables de entorno o usar una por defecto
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        
        # Si no hay API key, advertir en logs
        if self.api_key == "demo":
            logger.warning("Usando API key de demo para Alpha Vantage. La funcionalidad puede ser limitada.")
    
    async def get_stock_quote(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene la cotización actual de una acción.
        
        Args:
            symbol: El símbolo de la acción a consultar (por defecto: GPRK)
            
        Returns:
            Datos de la cotización de la acción
        """
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        return await self._make_request(params)
    
    async def get_brent_price(self) -> Dict[str, Any]:
        """
        Obtiene el precio actual del petróleo Brent.
        
        Returns:
            Datos del precio del Brent
        """
        # El símbolo para Brent crude oil es generalmente BZ=F o BRENT
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": "BZ=F",  # Símbolo para Brent crude oil futures
            "apikey": self.api_key
        }
        
        return await self._make_request(params)
    
    async def get_company_overview(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene información general de la compañía, incluyendo market cap.
        
        Args:
            symbol: El símbolo de la acción a consultar (por defecto: GPRK)
            
        Returns:
            Datos generales de la compañía
        """
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        return await self._make_request(params)
    
    async def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Realiza una solicitud a la API de Alpha Vantage.
        
        Args:
            params: Parámetros para la solicitud
            
        Returns:
            Respuesta de la API en formato JSON
            
        Raises:
            Exception: Si ocurre un error durante la solicitud
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()  # Lanza excepción para códigos 4xx/5xx
                
                data = response.json()
                
                # Verificar si hay un mensaje de error en la respuesta
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                    raise Exception(f"Alpha Vantage API error: {data['Error Message']}")
                
                # Verificar si se excedió el límite de solicitudes
                if "Note" in data and "call frequency" in data["Note"]:
                    logger.warning(f"Alpha Vantage API rate limit: {data['Note']}")
                
                return data
                
        except httpx.RequestError as e:
            logger.error(f"Error en la solicitud a Alpha Vantage: {str(e)}")
            raise Exception(f"Error en la conexión con Alpha Vantage: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error inesperado con Alpha Vantage: {str(e)}")
            raise 