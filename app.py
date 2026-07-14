import os
import smtplib
import pandas as pd
import streamlit as str_visual
import yfinance as yf

# ==========================================
# 📝 CONFIGURACIÓN DE CREDENCIALES Y ENTORNO
# ==========================================
REMITENTE = "asconexion@hotmail.com"  
CONTRASEÑA = "gigjctbnvuwsrtjm"    
DESTINATARIO = "lisaesm2017@gmail.com" 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6LnyXIBC8zFwmHJoNPlKTfRjCbKpQeARepvDn4G29weQg")

str_visual.set_page_config(page_title="Sistema SisFin", layout="wide")

ACTIVOS = {
    "BTC-USD": "Bitcoin - Oro digital, activo de reserva principal en Bitso.",
    "ETH-USD": "Ethereum - Infraestructura global de contratos inteligentes en Bitso.",
    "XRP-USD": "Ripple - Eficiencia en pagos transfronterizos y liquidez en Bitso.",
    "SOL-USD": "Solana - Blockchain de alta velocidad y bajas comisiones disponible en Bitso.",
    "ADA-USD": "Cardano - Red descentralizada enfocada en seguridad y asignación en Bitso.",
    "SNDK": "SanDisk / Western Digital - Almacenamiento y memoria flash esenciales.",
    "WDC": "Western Digital Corp. - Infraestructura de almacenamiento masivo.",
    "MU": "Micron Technology - Memorias DRAM y HBM críticas para IA.",
    "AMD": "Advanced Micro Devices - Procesadores y aceleradores de IA.",
    "DELL": "Dell Technologies - Servidores optimizados para IA."
}

# ==========================================
# 🛠️ FUNCIONES CORE Y CALCULADORA TÉCNICA
# ==========================================

def obtener_tipo_cambio_mxn():
    try:
        ticker = yf.Ticker("USDMXN=X")
        datos = ticker.history(period="1d")
        if not datos.empty:
            return float(datos['Close'].values[-1])
        return 20.00
    except Exception:
        return 20.00

tipo_cambio_mxn = obtener_tipo_cambio_mxn()

def calcular_rsi(serie_precios, periodo=14):
    if len(serie_precios) < periodo:
        return 50.0
    try:
        df = pd.DataFrame(serie_precios)
        delta = df.diff()
        ganancia = delta.clip(lower=0)
        pérdida = -1 * delta.clip(upper=0)
        ema_ganancia = ganancia.ewm(com=periodo-1, adjust=False).mean()
        ema_pérdida = pérdida.ewm(com=periodo-1, adjust=False).mean()
        rs = ema_ganancia / (ema_pérdida + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.values[-1])
    except Exception:
        return 50.0

def enviar_correo_html(asunto, contenido_html):
    try:
        msg = MIMEMultipart()
        msg['From'] = REMITENTE
        msg['To'] = DESTINATARIO
        msg['Subject'] = asunto
        msg.attach(MIMEText(contenido_html, 'html', 'utf-8'))
        server = smtplib.SMTP('://gmail.com', 587)
        server.starttls()  
        server.login(REMITENTE, CONTRASEÑA)
        server.sendmail(REMITENTE, DESTINATARIO, msg.as_string())
        server.quit()
        return True
    except Exception:
        return False

# ==========================================
# 📊 BARRA LATERAL (SIDEBAR): PORTAFOLIO Y CALCULADORA
# ==========================================
str_visual.sidebar.markdown("# 💼 Portafolio Virtual (Bitso)")
str_visual.sidebar.write("Ingresa tus compras para calcular tus ganancias reales en MXN:")

compras_usuario = {}
for simbolo in ACTIVOS.keys():
    if "-USD" in simbolo:
        nombre_corto = simbolo.replace("-USD", "")
        str_visual.sidebar.markdown(f"**🟢 {nombre_corto}**")
        monto_invertido = str_visual.sidebar.number_input(f"Monto Invertido (MXN) en {nombre_corto}", min_value=0.0, value=0.0, step=100.0, key=f"inv_{simbolo}")
        precio_compra = str_visual.sidebar.number_input(f"Precio de compra unitario (MXN)", min_value=0.0, value=0.0, step=10.0, key=f"px_{simbolo}")
        if monto_invertido > 0 and precio_compra > 0:
            compras_usuario[simbolo] = {"monto_mxn": monto_invertido, "precio_compra_mxn": precio_compra}

str_visual.sidebar.markdown("---")

# 🧮 NUEVA SECCIÓN: CALCULADORA DE INTERÉS COMPUESTO
str_visual.sidebar.markdown("# 🧮 Calculadora de Interés Compuesto")
capital_inicial = str_visual.sidebar.number_input("Capital Inicial (MXN)", min_value=0.0, value=1000.0, step=500.0)
aporte_mensual = str_visual.sidebar.number_input("Aporte Mensual (MXN)", min_value=0.0, value=500.0, step=100.0)
tasa_anual = str_visual.sidebar.number_input("Tasa Anual Esperada (%)", min_value=0.0, value=12.0, step=0.5)
anios_proyeccion = str_visual.sidebar.slider("Años a Proyectar", min_value=1, max_value=30, value=5)

# Cálculo matemático del interés compuesto
tasa_mensual = (tasa_anual / 100) / 12
meses_totales = anios_proyeccion * 12
capital_final = capital_inicial * ((1 + tasa_mensual) ** meses_totales)

for m in range(1, meses_totales + 1):
    capital_final += aporte_mensual * ((1 + tasa_mensual) ** (meses_totales - m))

str_visual.sidebar.metric("Monto Final Proyectado", f"${capital_final:,.2f} MXN")
str_visual.sidebar.markdown("---")

# ==========================================
# 📊 PROCESAMIENTO DE DATOS FINANCIEROS Y ALERTAS
# ==========================================
lista_resumen = []
datos_graficos = {}
metricas_tecnicas = {}
total_portafolio_actual = 0.0
total_portafolio_invertido = 0.0

# Contenedores dinámicos para almacenar alertas visuales y mostrarlas al inicio de la carga
alertas_compra = []
alertas_venta = []

for simbolo, descripcion in ACTIVOS.items():
    try:
        ticker = yf.Ticker(simbolo)
        historial = ticker.history(period="45d")
        if not historial.empty:
            precio_actual = float(historial['Close'].values[-1])
            precio_mxn = precio_actual * tipo_cambio_mxn
            rsi_actual = calcular_rsi(historial['Close'])
            historial_30d = historial.tail(30)
            p_max = float(historial_30d['High'].max())
            p_min = float(historial_30d['Low'].min())
            precios_lista = historial_30d['Close'].values
            p_inicial = float(precios_lista) if len(precios_lista) > 0 else precio_actual
            rendimiento = ((precio_actual - p_inicial) / (p_inicial + 1e-10)) * 100
            darvas_techo = p_max * 0.98
            darvas_piso = p_min * 1.02
            stop_loss_mxn = darvas_piso * 0.95 * tipo_cambio_mxn
            
            ganancia_texto = "$0.00 MXN"
            if simbolo in compras_usuario:
                unidades = compras_usuario[simbolo]["monto_mxn"] / compras_usuario[simbolo]["precio_compra_mxn"]
                valor_actual_mxn = unidades * precio_mxn
                ganancia_neta_mxn = valor_actual_mxn - compras_usuario[simbolo]["monto_mxn"]
                rendimiento_usuario = (ganancia_neta_mxn / compras_usuario[simbolo]["monto_mxn"]) * 100
                ganancia_texto = f"${ganancia_neta_mxn:,.2f} MXN ({rendimiento_usuario:.1f}%)"
                total_portafolio_invertido += compras_usuario[simbolo]["monto_mxn"]
                total_portafolio_actual += valor_actual_mxn
            
            recom_final = "RETENER"
            if rsi_actual <= 35: recom_final = "COMPRA"
            elif rsi_actual >= 65: recom_final = "VENDER"
            
            # ACTIVACIÓN DE ALERTAS VISUALES CRÍTICAS AUTOMÁTICAS
            nombre_limpio = simbolo.replace("-USD", "")
            if rsi_actual <= 30:
                alertas_compra.append(f"🔥 ¡Zona de COMPRA Crítica en {nombre_limpio}! El RSI está en {rsi_actual:.1f} (Sobreventa).")
            elif rsi_actual >= 70:
                alertas_venta.append(f"⚠️ ¡Alerta de VENTA en {nombre_limpio}! El RSI está en {rsi_actual:.1f} (Sobrecompra).")

            lista_resumen.append({"Activo": simbolo, "Precio MXN": f"${precio_mxn:,.2f}", "RSI (14d)": f"{rsi_actual:.1f}", "Mi Ganancia": ganancia_texto, "Sugerencia Tecnica": recom_final})
            datos_graficos[simbolo] = historial_30d['Close']
            metricas_tecnicas[simbolo] = {"max_mxn": p_max * tipo_cambio_mxn, "min_mxn": p_min * tipo_cambio_mxn, "actual_mxn": precio_mxn, "rsi": rsi_actual, "stop_loss_mxn": stop_loss_mxn, "descripcion": descripcion}
    except Exception:
        continue

df_matriz = pd.DataFrame(lista_resumen)

# ==========================================
# 🧱 INTERFAZ GRÁFICA: SISTEMA SISFIN
# ==========================================

str_visual.markdown("<h1 style='text-align: center; color: #1e3a8a;'>📊 Sistema SisFin</h1>", unsafe_allow_html=True)
str_visual.markdown(f"<p style='text-align: center; font-size: 16px; color: #64748b;'>Panel de Control Financiero Pro • <b>Tipo de Cambio: ${tipo_cambio_mxn:.2f} MXN</b></p>", unsafe_allow_html=True)
str_visual.markdown("---")

# DESPLEGAR LAS NOTIFICACIONES VISUALES AL INICIO SI EXISTEN ACTIVOS EN ZONAS CRÍTICAS
for msg_c in alertas_compra:
    str_visual.toast(msg_c, icon="🔥")
for msg_v in alertas_venta:
    str_visual.error(msg_v)

if total_portafolio_invertido > 0:
    str_visual.subheader("💼 Resumen Financiero de Tu Billetera")
    c_port1, c_port2, c_port3 = str_visual.columns(3)
    ganancia_total_neta = total_portafolio_actual - total_portafolio_invertido
    pct_total = (ganancia_total_neta / total_portafolio_invertido) * 100
    c_port1.metric("Total Invertido", f"${total_portafolio_invertido:,.2f} MXN")
    c_port2.metric("Valor Actual del Portafolio", f"${total_portafolio_actual:,.2f} MXN")
    c_port3.metric("Rendimiento Neto Total", f"${ganancia_total_neta:,.2f} MXN", f"{pct_total:.2f}%")
    str_visual.markdown("---")

# CREACIÓN DE LAS PESTAÑAS DEL SISTEMA
tab_matriz, tab_analisis = str_visual.tabs(["📋 MATRIZ DE CONTROL", "💡 DETALLE DE ACTIVOS Y TENDENCIAS"])

with tab_matriz:
    str_visual.subheader("📋 Resumen General de Activos")
    if not df_matriz.empty:
        str_visual.dataframe(df_matriz, use_container_width=True, hide_index=True)
    else:
        str_visual.warning("Esperando descarga de datos del mercado...")

with tab_analisis:
    str_visual.subheader("💡 Gráficos Nativos y Cajas Técnicas")
    for simbolo, tech in metricas_tecnicas.items():
        historial_precios = datos_graficos[simbolo]