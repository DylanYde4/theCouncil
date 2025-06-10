"""
Handlers personalizados para integrar los endpoints de GeoPark con el sistema de automatización.
"""
import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from src.interfaces.api.geopark_automation_collect.financial_data_service import FinancialDataService

logger = logging.getLogger(__name__)

# Instancia compartida del servicio
financial_service = FinancialDataService()

async def handle_system_test(
    params: Dict[str, Any],
    repository: Any = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handler de diagnóstico que no depende de servicios externos.
    Útil para verificar si el sistema de handlers funciona correctamente.
    
    Args:
        params: Parámetros de la solicitud
        repository: Repositorio de base de datos (no usado)
        
    Returns:
        Datos de diagnóstico básicos
    """
    logger.info("Ejecutando prueba de sistema")
    
    try:
        # Generamos datos estáticos que no requieren Alpha Vantage
        result = {
            "success": True,
            "system_time": datetime.now().isoformat(),
            "message": "El sistema de handlers está funcionando correctamente",
            "params_received": params,
            "handler": "handle_system_test"
        }
        
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error en handler de prueba: {str(e)}")
        return {
            "error": f"Error en prueba del sistema: {str(e)}",
            "error_detail": error_detail
        }

async def handle_stock_price(
    params: Dict[str, Any], 
    repository: Any = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handler personalizado para el endpoint de precio de acciones.
    
    Args:
        params: Parámetros de la solicitud
        repository: Repositorio de base de datos (no usado)
        
    Returns:
        Datos del precio de la acción
    """
    # Ignoramos el repositorio y usamos nuestro servicio directamente
    symbol = params.get("symbol", "GPRK")
    logger.info(f"Solicitando precio de acción para {symbol}")
    
    try:
        result = await financial_service.get_stock_price(symbol)
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener precio de acción: {str(e)}")
        return {
            "error": f"Error al obtener precio de acción: {str(e)}",
            "error_detail": error_detail
        }

async def handle_brent_price(
    params: Dict[str, Any], 
    repository: Any = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handler personalizado para el endpoint de precio de Brent.
    
    Args:
        params: Parámetros de la solicitud
        repository: Repositorio de base de datos (no usado)
        
    Returns:
        Datos del precio del Brent
    """
    # Ignoramos el repositorio y usamos nuestro servicio directamente
    logger.info("Solicitando precio de Brent")
    
    try:
        result = await financial_service.get_brent_price()
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener precio de Brent: {str(e)}")
        return {
            "error": f"Error al obtener precio de Brent: {str(e)}",
            "error_detail": error_detail
        }

async def handle_trading_volume(
    params: Dict[str, Any], 
    repository: Any = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handler personalizado para el endpoint de volumen de transacciones.
    
    Args:
        params: Parámetros de la solicitud
        repository: Repositorio de base de datos (no usado)
        
    Returns:
        Datos del volumen de transacciones
    """
    # Ignoramos el repositorio y usamos nuestro servicio directamente
    symbol = params.get("symbol", "GPRK")
    logger.info(f"Solicitando volumen de transacciones para {symbol}")
    
    try:
        result = await financial_service.get_trading_volume(symbol)
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener volumen de transacciones: {str(e)}")
        return {
            "error": f"Error al obtener volumen de transacciones: {str(e)}",
            "error_detail": error_detail
        }

async def handle_market_cap(
    params: Dict[str, Any], 
    repository: Any = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handler personalizado para el endpoint de capitalización de mercado.
    
    Args:
        params: Parámetros de la solicitud
        repository: Repositorio de base de datos (no usado)
        
    Returns:
        Datos de capitalización de mercado
    """
    # Ignoramos el repositorio y usamos nuestro servicio directamente
    symbol = params.get("symbol", "GPRK")
    logger.info(f"Solicitando capitalización de mercado para {symbol}")
    
    try:
        result = await financial_service.get_market_cap(symbol)
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener capitalización de mercado: {str(e)}")
        return {
            "error": f"Error al obtener capitalización de mercado: {str(e)}",
            "error_detail": error_detail
        }

async def handle_all_financial_data(
    params: Dict[str, Any], 
    repository: Any = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Handler personalizado para el endpoint de todos los datos financieros.
    
    Args:
        params: Parámetros de la solicitud
        repository: Repositorio de base de datos (no usado)
        
    Returns:
        Todos los datos financieros
    """
    # Ignoramos el repositorio y usamos nuestro servicio directamente
    symbol = params.get("symbol", "GPRK")
    logger.info(f"Solicitando todos los datos financieros para {symbol}")
    
    try:
        result = await financial_service.get_all_financial_data(symbol)
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener todos los datos financieros: {str(e)}")
        return {
            "error": f"Error al obtener todos los datos financieros: {str(e)}",
            "error_detail": error_detail
        } 