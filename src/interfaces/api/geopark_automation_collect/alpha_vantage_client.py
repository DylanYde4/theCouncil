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
        
        # Probar con diferentes símbolos para el Brent
        # Alpha Vantage no tiene un símbolo estándar para Brent, pero algunos símbolos comunes incluyen:
        # "BRENT", "BZ", "CB=F", "BRENTUSD"
        
        # Usaremos XBR como símbolo para Brent (usado en algunos exchanges)
        symbol = "BRENT"
        logger.info(f"Usando símbolo '{symbol}' para Brent")
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        # Registrar la URL que vamos a consultar (sin la API key)
        safe_params = params.copy()
        safe_params["apikey"] = "XXXXX"  # Ocultar la API key en los logs
        logger.debug(f"URL de consulta: {self.BASE_URL} con parámetros: {safe_params}")
        
        result = await self._make_request(params)
        
        # Si no funciona BRENT, intentar con un símbolo alternativo
        if "Global Quote" not in result or not result.get("Global Quote", {}).get("05. price"):
            logger.warning(f"No se encontraron datos para '{symbol}', intentando con 'BZ'")
            params["symbol"] = "BZ"
            result = await self._make_request(params)
            
            # Si tampoco funciona, intentar con otro símbolo
            if "Global Quote" not in result or not result.get("Global Quote", {}).get("05. price"):
                logger.warning(f"No se encontraron datos para 'BZ', intentando con 'UKOIL'")
                params["symbol"] = "UKOIL"
                result = await self._make_request(params)
                
                # Si ningún símbolo funciona, intentar con datos históricos
                if "Global Quote" not in result or not result.get("Global Quote", {}).get("05. price"):
                    logger.warning("No se encontraron datos actuales para ningún símbolo del Brent")
                    return await self.get_brent_historical_data()
        
        return result
    
    async def get_brent_historical_data(self) -> Dict[str, Any]:
        """
        Obtiene datos históricos del petróleo Brent.
        Se utiliza cuando no hay datos actuales disponibles.
        
        Returns:
            Datos históricos del precio del Brent
        """
        logger.info("Solicitando datos históricos del Brent")
        
        # Intentar con diferentes símbolos para datos históricos
        symbols = ["BRENT", "BZ", "UKOIL"]
        
        for symbol in symbols:
            logger.info(f"Intentando obtener datos históricos con símbolo '{symbol}'")
            
            # Usar la función TIME_SERIES_DAILY para obtener datos históricos
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": "compact",  # compact = últimos 100 días, full = hasta 20 años
                "apikey": self.api_key
            }
            
            # Registrar la URL que vamos a consultar (sin la API key)
            safe_params = params.copy()
            safe_params["apikey"] = "XXXXX"  # Ocultar la API key en los logs
            logger.debug(f"URL de consulta: {self.BASE_URL} con parámetros: {safe_params}")
            
            result = await self._make_request(params)
            
            # Verificar si hay datos históricos
            if "Time Series (Daily)" in result:
                time_series = result["Time Series (Daily)"]
                # Obtener la fecha más reciente (primera clave en el diccionario)
                if time_series:
                    latest_date = next(iter(time_series))
                    latest_data = time_series[latest_date]
                    
                    logger.info(f"Datos históricos encontrados para {symbol} en fecha {latest_date}")
                    
                    # Crear una respuesta en formato similar a Global Quote
                    historical_data = {
                        "Global Quote": {
                            "01. symbol": symbol,
                            "02. open": latest_data.get("1. open", "N/A"),
                            "03. high": latest_data.get("2. high", "N/A"),
                            "04. low": latest_data.get("3. low", "N/A"),
                            "05. price": latest_data.get("4. close", "N/A"),
                            "06. volume": latest_data.get("5. volume", "N/A"),
                            "07. latest trading day": latest_date,
                            "08. previous close": "N/A",  # No disponible directamente
                            "09. change": "0",  # No disponible directamente
                            "10. change percent": "0.00%",  # No disponible directamente
                            "source": "Alpha Vantage Historical Data"
                        }
                    }
                    
                    return historical_data
        
        # Si no se encontraron datos históricos
        logger.error("No se encontraron datos históricos para ningún símbolo del Brent")
        return {"error": "No hay datos históricos disponibles para el Brent"}
    
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