"""
Servicio para procesar y almacenar datos financieros de GeoPark.
"""
import logging
import json
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
    
    async def get_stock_price(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene el precio actual de una acción.
        
        Args:
            symbol: El símbolo de la acción (por defecto: GPRK)
            
        Returns:
            Datos del precio de la acción
        """
        # Obtener datos de Alpha Vantage
        quote_data = await self.alpha_vantage_client.get_stock_quote(symbol)
        
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
            logger.error(f"Datos de precio no disponibles para {symbol}")
            return {"error": f"Datos de precio no disponibles para {symbol}"}
    
    async def get_brent_price(self) -> Dict[str, Any]:
        """
        Obtiene el precio actual del petróleo Brent.
        
        Returns:
            Datos del precio del Brent
        """
        # Obtener datos de Alpha Vantage
        brent_data = await self.alpha_vantage_client.get_brent_price()
        
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
            logger.error("Datos de precio de Brent no disponibles")
            return {"error": "Datos de precio de Brent no disponibles"}
    
    async def get_trading_volume(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene el volumen de transacciones de una acción.
        
        Args:
            symbol: El símbolo de la acción (por defecto: GPRK)
            
        Returns:
            Datos del volumen de transacciones
        """
        # Obtener datos de Alpha Vantage
        quote_data = await self.alpha_vantage_client.get_stock_quote(symbol)
        
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
            logger.error(f"Datos de volumen no disponibles para {symbol}")
            return {"error": f"Datos de volumen no disponibles para {symbol}"}
    
    async def get_market_cap(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene la capitalización de mercado de una empresa.
        
        Args:
            symbol: El símbolo de la acción (por defecto: GPRK)
            
        Returns:
            Datos de capitalización de mercado
        """
        # Obtener datos de Alpha Vantage
        overview_data = await self.alpha_vantage_client.get_company_overview(symbol)
        
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
            logger.error(f"Datos de capitalización de mercado no disponibles para {symbol}")
            return {"error": f"Datos de capitalización de mercado no disponibles para {symbol}"}
    
    async def get_all_financial_data(self, symbol: str = "GPRK") -> Dict[str, Any]:
        """
        Obtiene todos los datos financieros en una sola llamada.
        
        Args:
            symbol: El símbolo de la acción (por defecto: GPRK)
            
        Returns:
            Todos los datos financieros
        """
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
                # Registrar que el almacenamiento no está disponible
                logger.warning("Vercel Blob Storage no disponible para guardar datos financieros.")
                return None
        except Exception as e:
            logger.error(f"Error al guardar datos financieros: {str(e)}")
            return None 