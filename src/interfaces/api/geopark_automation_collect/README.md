# GeoPark Financial Data Automation

## Descripción
Sistema de automatización para extracción, transformación y almacenamiento de datos financieros de GeoPark con integración a Alpha Vantage API.

## Configuración

### API Key de Alpha Vantage
Para utilizar esta automatización, es necesario obtener una API Key de Alpha Vantage:

1. Visita [Alpha Vantage](https://www.alphavantage.co/support/#api-key) y regístrate para obtener una API key gratuita
2. Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:
   ```
   ALPHA_VANTAGE_API_KEY=tu_api_key_aquí
   ```

### Almacenamiento Vercel Blob (opcional)
Para utilizar Vercel Blob Storage:

1. Configura tu proyecto con Vercel
2. Añade la siguiente variable de entorno:
   ```
   BLOB_READ_WRITE_TOKEN=tu_token_aquí
   ```

## Endpoints

La automatización expone los siguientes endpoints:

- `GET /api/geopark/stock-price` - Obtiene el precio actual de las acciones de GeoPark
- `GET /api/geopark/brent-price` - Obtiene el precio actual del petróleo Brent
- `GET /api/geopark/trading-volume` - Obtiene el volumen de acciones transadas
- `GET /api/geopark/market-cap` - Obtiene la capitalización de mercado de GeoPark
- `GET /api/geopark/all-data` - Obtiene todos los datos anteriores en una sola llamada

## Uso

1. Inicia la aplicación con `python -m src.main`
2. Accede a los endpoints mediante un navegador o herramienta como curl/Postman:
   ```
   curl http://localhost:8000/api/geopark/all-data
   ```

## Parámetros

Todos los endpoints (excepto `/brent-price`) aceptan el parámetro opcional `symbol` para especificar un símbolo diferente al predeterminado "GPRK":

```
GET /api/geopark/stock-price?symbol=AAPL
``` 