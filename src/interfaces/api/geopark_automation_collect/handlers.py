"""
Controladores para la API de datos financieros de GeoPark.
"""
import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query

from src.interfaces.api.geopark_automation_collect.financial_data_service import FinancialDataService

# Crear el router de FastAPI
router = APIRouter(prefix="/api/geopark", tags=["GeoPark Financial Data"])

# Logger
logger = logging.getLogger(__name__)

# Dependencia para obtener el servicio de datos financieros
def get_financial_data_service():
    """Dependencia para obtener el servicio de datos financieros."""
    return FinancialDataService()

@router.get("/test")
async def get_test():
    """
    Endpoint de prueba simple que no depende de servicios externos.
    """
    try:
        logger.info("Ejecutando endpoint de prueba directa")
        return {
            "success": True,
            "time": datetime.now().isoformat(),
            "message": "Endpoint de prueba está funcionando correctamente",
            "endpoint": "/api/geopark/test"
        }
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error en endpoint de prueba: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"error": f"Error en prueba: {str(e)}", "trace": error_detail}
        )

@router.get("/stock-price")
async def get_stock_price(
    symbol: str = Query("GPRK", description="Símbolo de la acción"),
    service: FinancialDataService = Depends(get_financial_data_service)
):
    """
    Obtiene el precio actual de las acciones de GeoPark.
    
    Args:
        symbol: Símbolo de la acción (por defecto: GPRK)
        service: Servicio de datos financieros
        
    Returns:
        Datos del precio de la acción
    """
    try:
        logger.info(f"Solicitud de precio de acción para {symbol}")
        result = await service.get_stock_price(symbol)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener precio de acción: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"error": f"Error al obtener precio de acción: {str(e)}", "trace": error_detail}
        )

@router.get("/brent-price")
async def get_brent_price(
    service: FinancialDataService = Depends(get_financial_data_service)
):
    """
    Obtiene el precio actual del petróleo Brent.
    
    Args:
        service: Servicio de datos financieros
        
    Returns:
        Datos del precio del Brent
    """
    try:
        logger.info("Solicitud de precio de Brent")
        result = await service.get_brent_price()
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener precio de Brent: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"error": f"Error al obtener precio de Brent: {str(e)}", "trace": error_detail}
        )

@router.get("/trading-volume")
async def get_trading_volume(
    symbol: str = Query("GPRK", description="Símbolo de la acción"),
    service: FinancialDataService = Depends(get_financial_data_service)
):
    """
    Obtiene el volumen de transacciones de GeoPark.
    
    Args:
        symbol: Símbolo de la acción (por defecto: GPRK)
        service: Servicio de datos financieros
        
    Returns:
        Datos del volumen de transacciones
    """
    try:
        logger.info(f"Solicitud de volumen de transacciones para {symbol}")
        result = await service.get_trading_volume(symbol)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener volumen de transacciones: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"error": f"Error al obtener volumen de transacciones: {str(e)}", "trace": error_detail}
        )

@router.get("/market-cap")
async def get_market_cap(
    symbol: str = Query("GPRK", description="Símbolo de la acción"),
    service: FinancialDataService = Depends(get_financial_data_service)
):
    """
    Obtiene la capitalización de mercado de GeoPark.
    
    Args:
        symbol: Símbolo de la acción (por defecto: GPRK)
        service: Servicio de datos financieros
        
    Returns:
        Datos de capitalización de mercado
    """
    try:
        logger.info(f"Solicitud de capitalización de mercado para {symbol}")
        result = await service.get_market_cap(symbol)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener capitalización de mercado: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"error": f"Error al obtener capitalización de mercado: {str(e)}", "trace": error_detail}
        )

@router.get("/all-data")
async def get_all_financial_data(
    symbol: str = Query("GPRK", description="Símbolo de la acción"),
    service: FinancialDataService = Depends(get_financial_data_service)
):
    """
    Obtiene todos los datos financieros de GeoPark.
    
    Args:
        symbol: Símbolo de la acción (por defecto: GPRK)
        service: Servicio de datos financieros
        
    Returns:
        Todos los datos financieros
    """
    try:
        logger.info(f"Solicitud de todos los datos financieros para {symbol}")
        result = await service.get_all_financial_data(symbol)
        
        if any(key in data for data in result.values() for key in ["error"]):
            logger.warning(f"Algunos datos financieros no están disponibles para {symbol}")
            
        return result
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.exception(f"Error al obtener todos los datos financieros: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"error": f"Error al obtener todos los datos financieros: {str(e)}", "trace": error_detail}
        ) 