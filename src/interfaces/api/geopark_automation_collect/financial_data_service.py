"""
Servicio para procesar y almacenar datos financieros de GeoPark.
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from src.interfaces.api.geopark_automation_collect.alpha_vantage_client import AlphaVantageClient

try:
    from src.infrastructure.storage.blob_storage import BlobStorageAdapter
    BLOB_STORAGE_AVAILABLE = True
except ImportError:
    logging.warning("Vercel Blob Storage no disponible. Se usará respaldo local.")
    BLOB_STORAGE_AVAILABLE = False

logger = logging.getLogger(__name__)

class FinancialDataService:
    """
    Servicio para procesar y almacenar datos financieros.
    Utiliza Alpha Vantage para obtener datos y Vercel Blob Storage para almacenarlos.
    """
    
    def __init__(self):
        """Inicializa el servicio de datos financieros."""
        self.alpha_vantage_client = AlphaVantageClient()
        # Asegurar que el directorio de datos existe
        os.makedirs("data/automations", exist_ok=True)
    
    async def get_stock_price(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene el precio actual de una acción.
        
        Args:
            symbol: El símbolo de la acción (por defecto: GPRK)
            
        Returns:
            Datos del precio de la acción
        """
        try:
            logger.info(f"Obteniendo datos de precio para {symbol} desde Alpha Vantage")
            # Obtener datos de Alpha Vantage
            quote_data = await self.alpha_vantage_client.get_stock_quote(symbol)
            logger.debug(f"Datos recibidos de Alpha Vantage: {quote_data}")
            
            # Extraer los datos relevantes
            if "Global Quote" in quote_data:
                price_data = {
                    "symbol": symbol,
                    "price": quote_data["Global Quote"].get("05. price", "N/A"),
                    "change": quote_data["Global Quote"].get("09. change", "N/A"),
                    "change_percent": quote_data["Global Quote"].get("10. change percent", "N/A"),
                    "timestamp": datetime.now().isoformat(),
                    "source": "Alpha Vantage"
                }
                
                # Guardar datos en almacenamiento
                await self._save_financial_data(f"stock_price_{symbol}", price_data)
                
                return price_data
            else:
                logger.error(f"Datos de precio no disponibles para {symbol}. Respuesta: {quote_data}")
                return {"error": f"Datos de precio no disponibles para {symbol}"}
        except Exception as e:
            logger.exception(f"Error en get_stock_price para {symbol}: {str(e)}")
            return {"error": f"Error al obtener precio de acción: {str(e)}"}
    
    async def get_brent_price(self) -> Dict[str, Any]:
        """
        Obtiene el precio actual del petróleo Brent.
        
        Returns:
            Datos del precio del Brent
        """
        try:
            logger.info("Obteniendo datos de precio del Brent desde Alpha Vantage")
            # Obtener datos de Alpha Vantage
            brent_data = await self.alpha_vantage_client.get_brent_price()
            logger.debug(f"Datos recibidos de Alpha Vantage: {brent_data}")
            
            # Extraer los datos relevantes
            if "Global Quote" in brent_data:
                price_data = {
                    "symbol": "BRENT",
                    "price": brent_data["Global Quote"].get("05. price", "N/A"),
                    "change": brent_data["Global Quote"].get("09. change", "N/A"),
                    "change_percent": brent_data["Global Quote"].get("10. change percent", "N/A"),
                    "timestamp": datetime.now().isoformat(),
                    "source": "Alpha Vantage"
                }
                
                # Guardar datos en almacenamiento
                await self._save_financial_data("brent_price", price_data)
                
                return price_data
            else:
                logger.error(f"Datos de precio de Brent no disponibles. Respuesta: {brent_data}")
                return {"error": "Datos de precio de Brent no disponibles"}
        except Exception as e:
            logger.exception(f"Error en get_brent_price: {str(e)}")
            return {"error": f"Error al obtener precio de Brent: {str(e)}"}
    
    async def get_trading_volume(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene el volumen de transacciones de una acción.
        
        Args:
            symbol: El símbolo de la acción (por defecto: GPRK)
            
        Returns:
            Datos del volumen de transacciones
        """
        try:
            logger.info(f"Obteniendo datos de volumen para {symbol} desde Alpha Vantage")
            # Obtener datos de Alpha Vantage
            quote_data = await self.alpha_vantage_client.get_stock_quote(symbol)
            logger.debug(f"Datos recibidos de Alpha Vantage: {quote_data}")
            
            # Extraer los datos relevantes
            if "Global Quote" in quote_data:
                volume_data = {
                    "symbol": symbol,
                    "volume": quote_data["Global Quote"].get("06. volume", "N/A"),
                    "timestamp": datetime.now().isoformat(),
                    "source": "Alpha Vantage"
                }
                
                # Guardar datos en almacenamiento
                await self._save_financial_data(f"trading_volume_{symbol}", volume_data)
                
                return volume_data
            else:
                logger.error(f"Datos de volumen no disponibles para {symbol}. Respuesta: {quote_data}")
                return {"error": f"Datos de volumen no disponibles para {symbol}"}
        except Exception as e:
            logger.exception(f"Error en get_trading_volume para {symbol}: {str(e)}")
            return {"error": f"Error al obtener volumen de transacciones: {str(e)}"}
    
    async def get_market_cap(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene la capitalización de mercado de una empresa.
        
        Args:
            symbol: El símbolo de la acción (por defecto: GPRK)
            
        Returns:
            Datos de capitalización de mercado
        """
        try:
            logger.info(f"Obteniendo datos de capitalización de mercado para {symbol} desde Alpha Vantage")
            # Obtener datos de Alpha Vantage
            overview_data = await self.alpha_vantage_client.get_company_overview(symbol)
            logger.debug(f"Datos recibidos de Alpha Vantage: {overview_data}")
            
            # Extraer los datos relevantes
            if "MarketCapitalization" in overview_data:
                market_cap_data = {
                    "symbol": symbol,
                    "market_cap": overview_data.get("MarketCapitalization", "N/A"),
                    "name": overview_data.get("Name", symbol),
                    "sector": overview_data.get("Sector", "N/A"),
                    "industry": overview_data.get("Industry", "N/A"),
                    "timestamp": datetime.now().isoformat(),
                    "source": "Alpha Vantage"
                }
                
                # Guardar datos en almacenamiento
                await self._save_financial_data(f"market_cap_{symbol}", market_cap_data)
                
                return market_cap_data
            else:
                logger.error(f"Datos de capitalización de mercado no disponibles para {symbol}. Respuesta: {overview_data}")
                return {"error": f"Datos de capitalización de mercado no disponibles para {symbol}"}
        except Exception as e:
            logger.exception(f"Error en get_market_cap para {symbol}: {str(e)}")
            return {"error": f"Error al obtener capitalización de mercado: {str(e)}"}
    
    async def get_all_financial_data(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene todos los datos financieros en una sola llamada.
        
        Args:
            symbol: El símbolo de la acción (por defecto: GPRK)
            
        Returns:
            Todos los datos financieros
        """
        try:
            logger.info(f"Obteniendo todos los datos financieros para {symbol}")
            # Obtener todos los datos en paralelo sería más eficiente, pero por simplicidad,
            # los obtenemos secuencialmente
            stock_price = await self.get_stock_price(symbol)
            brent_price = await self.get_brent_price()
            trading_volume = await self.get_trading_volume(symbol)
            market_cap = await self.get_market_cap(symbol)
            
            # Combinar todos los datos
            all_data = {
                "stock_price": stock_price,
                "brent_price": brent_price,
                "trading_volume": trading_volume,
                "market_cap": market_cap,
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardar datos combinados en almacenamiento
            await self._save_financial_data(f"all_financial_data_{symbol}", all_data)
            
            return all_data
        except Exception as e:
            logger.exception(f"Error en get_all_financial_data para {symbol}: {str(e)}")
            return {"error": f"Error al obtener todos los datos financieros: {str(e)}"}
    
    async def _save_financial_data(self, key: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Guarda datos financieros en almacenamiento.
        Utiliza Vercel Blob Storage si está disponible, de lo contrario, registra un mensaje.
        
        Args:
            key: Clave para identificar los datos
            data: Datos a guardar
            
        Returns:
            URL de almacenamiento si está disponible, None en caso contrario
        """
        try:
            if BLOB_STORAGE_AVAILABLE and BlobStorageAdapter.is_available():
                # Guardar en Vercel Blob Storage
                url = await BlobStorageAdapter.save_json(key, data)
                logger.info(f"Datos financieros guardados en Blob Storage: {url}")
                return url
            else:
                # Guardar en archivo local
                file_path = f"data/automations/geopark_financial_data.json"
                logger.info(f"Guardando datos financieros en archivo local: {file_path}")
                try:
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=2)
                    logger.info(f"Datos guardados correctamente en {file_path}")
                except Exception as file_error:
                    logger.error(f"Error al guardar en archivo local: {str(file_error)}")
                return None
        except Exception as e:
            logger.exception(f"Error al guardar datos financieros: {str(e)}")
            return None 