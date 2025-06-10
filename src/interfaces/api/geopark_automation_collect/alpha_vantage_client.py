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
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        
        # Si no hay API key, advertir en logs
        if not self.api_key:
            logger.warning("No se encontró ALPHA_VANTAGE_API_KEY en las variables de entorno.")
            self.api_key = "demo"  # Usar demo como último recurso
            logger.warning("Se usará la clave 'demo' que tiene funcionalidad muy limitada (5 llamadas por minuto, 500 por día).")
    
    async def get_stock_quote(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene la cotización actual de una acción.
        
        Args:
            symbol: El símbolo de la acción a consultar (por defecto: GPRK)
            
        Returns:
            Datos de la cotización de la acción
        """
        logger.info(f"Solicitando cotización para {symbol}")
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        # Registrar la URL que vamos a consultar (sin la API key)
        safe_params = params.copy()
        safe_params["apikey"] = "XXXXX"  # Ocultar la API key en los logs
        logger.debug(f"URL de consulta: {self.BASE_URL} con parámetros: {safe_params}")
        
        return await self._make_request(params)
    
    async def get_brent_price(self) -> Dict[str, Any]:
        """
        Obtiene el precio actual del petróleo Brent.
        
        Returns:
            Datos del precio del Brent
        """
        logger.info("Solicitando precio del Brent")
        # El símbolo para Brent crude oil es generalmente BZ=F o BRENT
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": "BZ=F",  # Símbolo para Brent crude oil futures
            "apikey": self.api_key
        }
        
        # Registrar la URL que vamos a consultar (sin la API key)
        safe_params = params.copy()
        safe_params["apikey"] = "XXXXX"  # Ocultar la API key en los logs
        logger.debug(f"URL de consulta: {self.BASE_URL} con parámetros: {safe_params}")
        
        return await self._make_request(params)
    
    async def get_company_overview(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene información general de la compañía, incluyendo market cap.
        
        Args:
            symbol: El símbolo de la acción a consultar (por defecto: GPRK)
            
        Returns:
            Datos generales de la compañía
        """
        logger.info(f"Solicitando información general para {symbol}")
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        # Registrar la URL que vamos a consultar (sin la API key)
        safe_params = params.copy()
        safe_params["apikey"] = "XXXXX"  # Ocultar la API key en los logs
        logger.debug(f"URL de consulta: {self.BASE_URL} con parámetros: {safe_params}")
        
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
            logger.debug(f"Iniciando solicitud a Alpha Vantage")
            
            async with httpx.AsyncClient() as client:
                # Hacer la solicitud a la API
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()  # Lanza excepción para códigos 4xx/5xx
                
                data = response.json()
                logger.debug(f"Respuesta recibida de Alpha Vantage: {data}")
                
                # Verificar si hay un mensaje de error en la respuesta
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                    raise Exception(f"Alpha Vantage API error: {data['Error Message']}")
                
                # Verificar si se excedió el límite de solicitudes
                if "Note" in data and "call frequency" in data["Note"]:
                    logger.warning(f"Alpha Vantage API rate limit: {data['Note']}")
                
                return data
                
        except httpx.RequestError as e:
            logger.exception(f"Error en la solicitud a Alpha Vantage: {str(e)}")
            raise Exception(f"Error en la conexión con Alpha Vantage: {str(e)}")
        
        except Exception as e:
            logger.exception(f"Error inesperado con Alpha Vantage: {str(e)}")
            raise 