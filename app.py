import os
import smtplib
import pandas as pd
import streamlit as str_visual
import yfinance as yf
import plotly.graph_objects as go
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai

# ==========================================
# 📝 CONFIGURACIÓN DE CREDENCIALES Y ENTORNO
# ==========================================
REMITENTE = "asconektion2026@gmail.com"  
CONTRASEÑA = "gigjctbnvuwsrtjm"   
DESTINATARIO = "lisaesm2017@gmail.com" 

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Configuración de página con un layout limpio y moderno
str_visual.set_page_config(page_title="SisFin - Tablero de Inversiones AI", layout="wide")

# Tus activos tecnológicos clave
ACTIVOS = {
    "SNDK": "SanDisk / Western Digital - Almacenamiento y memoria flash esenciales.",
    "WDC": "Western Digital Corp. - Infraestructura de almacenamiento masivo y discos duros para data centers.",
    "MU": "Micron Technology - Memorias DRAM y HBM críticas para el entrenamiento de modelos de IA.",
    "AMD": "Advanced Micro Devices - Procesadores y aceleradores de IA (GPUs de arquitectura abierta).",
    "MRVL": "Marvell Technology - Chips de conectividad y redes de alta velocidad para centros de datos.",
    "ALAB": "Astera Labs - Soluciones de conectividad por conectores de silicio (PCIe/CXL) para la nube de IA.",
    "LRCX": "Lam Research Corp. - Equipos de fabricación y grabado para la industria de semiconductores de vanguardia.",
    "LITE": "Lumentum Holdings - Componentes ópticos y fotónica para la velocidad de redes ópticas.",
    "INTC": "Intel Corporation - Fabricación de silicio, fundiciones (foundries) y procesadores x86.",
    "DELL": "Dell Technologies - Servidores optimizados para IA a gran escala y soluciones enterprise de computación."
}

# Estilos visuales optimizados para destacar las Cajas de Darvas y Stop Loss
str_visual.markdown("""
    <style>
    .darvas-container {
        background-color: #1e293b;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #475569;
        margin-top: 10px;
    }
    .darvas-title {
        font-size: 0.95em;
        font-weight: bold;
        color: #38bdf8;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📈 FUNCIONES AUXILIARES Y ALGORITMOS
# ==========================================

def obtener_tipo_cambio_mxn():
    try:
        ticker = yf.Ticker("USDMXN=X")
        datos = ticker.history(period="1d")
        if not datos.empty:
            return datos['Close'].iloc[-1]
        return 20.00
    except Exception:
        return 20.00

def enviar_correo_html(asunto, contenido_html):
    try:
        msg = MIMEMultipart()
        msg['From'] = REMITENTE
        msg['To'] = DESTINATARIO
        msg['Subject'] = asunto
        msg.attach(MIMEText(contenido_html, 'html', 'utf-8'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  
        server.login(REMITENTE, CONTRASEÑA)
        server.sendmail(REMITENTE, DESTINATARIO, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        str_visual.error(f"Error al enviar el correo: {e}")
        return False

# --- ALGORITMO INTEGRADO: CAJA DE DARVAS ---
def calcular_caja_darvas(historial_df):
    """
    Calcula matemáticamente el Techo, Suelo y Stop Loss usando la teoría de Cajas de Nicolas Darvas
    basado en los últimos 30 días de mercado.
    """
    if historial_df.empty or len(historial_df) < 5:
        return {"techo": 0.0, "suelo": 0.0, "stop_loss": 0.0, "estado": "Consolidación"}
    
    # Nicolas Darvas buscaba los máximos y mínimos más significativos del periodo para delimitar la caja
    techo = historial_df['High'].max()
    suelo = historial_df['Low'].min()
    precio_actual = historial_df['Close'].iloc[-1]
    
    # El Stop Loss de seguridad se establece tradicionalmente justo un 1% o 2% por debajo del suelo de la caja
    stop_loss = suelo * 0.985
    
    # Determinamos la posición actual con respecto a la caja
    if precio_actual >= (techo * 0.98):
        estado = "Ruptura Alcista (Techo)"
    elif precio_actual <= (suelo * 1.02):
        estado = "Suelo Crítico (Riesgo)"
    else:
        estado = "Dentro de la Caja"
        
    return {
        "techo": techo,
        "suelo": suelo,
        "stop_loss": stop_loss,
        "estado": estado
    }

def analizar_con_ia(simbolo, precio, datos_empresa, darvas_metrics):
    """
    Comité híbrido de IA potenciado con los datos de precios de la Caja de Darvas.
    """
    instrucciones_expertas = (
        "Actúa como un comité de inversión híbrido compuesto por Warren Buffett y Leopold Aschenbrenner. "
        "Analiza el siguiente activo financiero combinando el Value Investing (Buffett: ventajas competitivas, "
        "estabilidad, valor intrínseco) con la visión macro-tecnológica exponencial (Aschenbrenner: AGI, "
        "infraestructura del futuro, centros de datos, semiconductores y crecimiento exponencial). "
        "Adicionalmente, incorpora los límites técnicos de la Caja de Darvas y el Stop Loss calculados para este activo. "
        "Al final de tu análisis, obligatoriamente escribe en una línea separada tu veredicto con este formato exacto: "
        "'RECOMENDACIÓN FINAL: COMPRA' o 'RECOMENDACIÓN FINAL: RETENER' o 'RECOMENDACIÓN FINAL: VENDER'. "
        "En la siguiente línea escribe: 'RIESGO: BAJO', 'RIESGO: MEDIO', 'RIESGO: ALTO' o 'RIESGO: EXTREMO'."
    )
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            f"Activo: {simbolo}\n"
            f"Precio Actual: ${precio:.2f} USD\n"
            f"Contexto de la Empresa: {datos_empresa}\n"
            f"Métricas Técnicas de la Caja de Darvas:\n"
            f"- Techo de la Caja: ${darvas_metrics['techo']:.2f} USD\n"
            f"- Suelo de la Caja (Soporte): ${darvas_metrics['suelo']:.2f} USD\n"
            f"- Stop Loss de Darvas sugerido: ${darvas_metrics['stop_loss']:.2f} USD\n"
            f"- Estado técnico actual: {darvas_metrics['estado']}\n\n"
            f"¿Cuál es tu análisis estratégico y técnico para hoy?"
        )
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'system_instruction': instrucciones_expertas}
        )
        return response.text
    except Exception as e:
        return f"Error en análisis de IA: {e}\nRECOMENDACIÓN FINAL: RETENER\nRIESGO: MEDIO"

def interpretar_grafica_ia(simbolo, maximo, minimo, actual, rendimiento):
    instrucciones = (
        "Eres un analista técnico de gráficos financieros. Analiza el comportamiento de los últimos 30 días "
        "de forma muy breve, directa y profesional (máximo 3 líneas de texto). "
        "Explica qué significa que el precio actual esté cerca de su máximo o mínimo, o qué nos dice el "
        "rendimiento porcentual reciente observado en este periodo."
    )
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (f"Activo: {simbolo}\nHistorial 30 días:\n- Máximo: ${maximo:.2f} USD\n- Mínimo: ${minimo:.2f} USD"
                  f"\n- Precio Actual: ${actual:.2f} USD\n- Rendimiento en el periodo: {rendimiento:.2f}%\n"
                  f"Escribe una interpretación concisa de la gráfica para un inversionista no técnico.")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'system_instruction': instrucciones}
        )
        return response.text
    except Exception:
        return "Interpretación gráfica temporalmente no disponible."

def obtener_noticias_y_consejo():
    instrucciones_noticias = (
        "Actúas como un Analista Financiero Senior Global. Genera un reporte resumido de las 4 noticias macroeconómicas "
        "y tecnológicas más importantes/recientes y futuras tendencias (geopolítica, tasas de interés, semiconductores, "
        "infraestructura AGI) que estén afectando los mercados de inversión globales. "
        "Formato obligatorio: Escribe la Noticia 1, luego pon el separador '###', luego la Noticia 2, luego '###', "
        "luego la Noticia 3, luego '###', luego la Noticia 4, luego el separador '###' y finaliza con el Consejo Estratégico Global."
    )
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = "Enumera tus 4 noticias financieras cruciales separadas por '###' and tu consejo final."
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'system_instruction': instrucciones_noticias}
        )
        return response.text
    except Exception as e:
        return f"Error###Error###Error###Error###No se pudieron cargar las noticias: {e}"


# ==========================================
# 💻 INTERFAZ GRÁFICA DE USUARIO (STREAMLIT)
# ==========================================

tipo_cambio_mxn = obtener_tipo_cambio_mxn()

str_visual.markdown("# 📊 PROYECTO SISFIN")
str_visual.markdown(f"### `Tablero de Inversión Inteligente` — *Métricas Avanzadas USD / MXN* (Dólar hoy: **${tipo_cambio_mxn:.2f} MXN**)")
str_visual.markdown("---")

str_visual.sidebar.header("⚙️ Centro de Operaciones")
str_visual.sidebar.markdown(f"**Divisa Base:** USD 🇺🇸<br>**Divisa Local:** MXN 🇲🇽<br>TC: `${tipo_cambio_mxn:.2f}`", unsafe_allow_html=True)
str_visual.sidebar.markdown("---")

str_visual.subheader("🌐 Panorama Macroeconómico Diario")

with str_visual.spinner("Estructurando cuadrante de noticias de mercado..."):
    raw_noticias = obtener_noticias_y_consejo()
    partes_noticias = raw_noticias.split('###')
    
    if len(partes_noticias) >= 5:
        n1, n2, n3, n4, consejo_global = [p.strip() for p in partes_noticias[:5]]
    else:
        n1 = n2 = n3 = n4 = "Noticia temporalmente no disponible."
        consejo_global = raw_noticias

    f1_col1, f1_col2 = str_visual.columns(2)
    with f1_col1:
        with str_visual.container(border=True):
            str_visual.markdown("##### 📰 Noticia Destacada 1")
            str_visual.write(n1)
    with f1_col2:
        with str_visual.container(border=True):
            str_visual.markdown("##### 📰 Noticia Destacada 2")
            str_visual.write(n2)
            
    f2_col1, f2_col2 = str_visual.columns(2)
    with f2_col1:
        with str_visual.container(border=True):
            str_visual.markdown("##### 📰 Noticia Destacada 3")
            str_visual.write(n3)
    with f2_col2:
        with str_visual.container(border=True):
            str_visual.markdown("##### 📰 Noticia Destacada 4")
            str_visual.write(n4)

    str_visual.info(f"💡 **Consejo Estratégico del Comité:** {consejo_global}")

str_visual.markdown("---")

lista_resumen = []
html_bloques_activos = ""
datos_graficos = {}
metricas_tecnicas = {}
metricas_darvas = {}  # Guardaremos los cálculos de Darvas para usarlos en el gráfico y correo

progreso_texto = str_visual.empty()
barra_progreso = str_visual.progress(0)
total_activos = len(ACTIVOS)

for i, (simbolo, descripcion) in enumerate(ACTIVOS.items()):
    progreso_texto.markdown(f"🔄 Analizando métricas y tendencias gráficas para: **{simbolo}**...")
    historial_30d = pd.DataFrame()
    max_30d = min_30d = rendimiento_30d = 0.0
    
    try:
        ticker = yf.Ticker(simbolo)
        historial_30d = ticker.history(period="30d")
        precio_actual = ticker.info.get('regularMarketPrice') if historial_30d.empty else historial_30d['Close'].iloc[-1]
        if precio_actual is None: precio_actual = 0.0
        
        if not historial_30d.empty:
            max_30d = historial_30d['Close'].max()
            min_30d = historial_30d['Close'].min()
            precio_inicial = historial_30d['Close'].iloc[0]
            rendimiento_30d = ((precio_actual - precio_inicial) / precio_inicial) * 100
    except Exception:
        precio_actual = 0.0
        
    precio_mxn = precio_actual * tipo_cambio_mxn
    
    # 1. Calculamos la Caja de Darvas matemáticamente
    darvas_res = calcular_caja_darvas(historial_30d)
    metricas_darvas[simbolo] = darvas_res
    
    # 2. Enviamos los datos de Darvas a la IA para el veredicto definitivo
    analisis = analizar_con_ia(simbolo, precio_actual, descripcion, darvas_res)
    
    rec_final = "RETENER"
    riesgo_final = "MEDIO"
    for linea in analisis.split('\n'):
        if "RECOMENDACIÓN FINAL:" in linea:
            rec_final = linea.split("RECOMENDACIÓN FINAL:")[-1].strip()
        if "RIESGO:" in linea:
            riesgo_final = linea.split("RIESGO:")[-1].strip()
            
    lista_resumen.append({
        "Ticker": simbolo,
        "Precio USD": f"${precio_actual:.2f} USD",
        "Precio MXN": f"${precio_mxn:.2f} MXN",
        "Recomendación": rec_final,
        "Nivel de Riesgo": riesgo_final,
        "analisis_raw": analisis
    })
    
    datos_graficos[simbolo] = historial_30d
    metricas_tecnicas[simbolo] = {
        "max": max_30d,
        "min": min_30d,
        "rendimiento": rendimiento_30d,
        "actual": precio_actual
    }
    barra_progreso.progress((i + 1) / total_activos)

progreso_texto.empty()
barra_progreso.empty()

# --- TABLA DE RESUMEN EJECUTIVO ---
str_visual.subheader("📋 Matriz de Control y Advertencias de Inversión")
df_resumen = pd.DataFrame(lista_resumen)
df_mostrar = df_resumen[["Ticker", "Precio USD", "Precio MXN", "Recomendación", "Nivel de Riesgo"]]

def colorear_celdas(val):
    if "COMPRA" in val:
        return 'background-color: #d1fae5; color: #065f46; font-weight: bold; border-radius: 4px;' 
    elif "VENDER" in val:
        return 'background-color: #fee2e2; color: #991b1b; font-weight: bold; border-radius: 4px;' 
    elif "RETENER" in val:
        return 'background-color: #fef3c7; color: #92400e; font-weight: bold; border-radius: 4px;' 
    return ''

df_estilizado = df_mostrar.style.map(colorear_celdas, subset=['Recomendación'])
str_visual.dataframe(df_estilizado, use_container_width=True, hide_index=True)

str_visual.markdown("---")

# --- BLOQUE DE ANÁLISIS DETALLADO POR ACTIVO ---
str_visual.subheader("💡 Análisis Profundo e Interpretación de Tendencias (Caja de Darvas Integrada)")

for item in lista_resumen:
    simbolo = item["Ticker"]
    p_usd = item["Precio USD"]
    p_mxn = item["Precio MXN"]
    rec = item["Recomendación"]
    riesgo = item["Nivel de Riesgo"]
    analisis_completo = item["analisis_raw"]
    historial_30d = datos_graficos[simbolo]
    tech = metricas_tecnicas[simbolo]
    d_vals = metricas_darvas[simbolo] # Traemos los cálculos de Darvas para este activo

    with str_visual.expander(f"🎯 {simbolo} — Veredicto: {rec} ({p_usd} / {p_mxn})"):
        col_metricas, col_grafico = str_visual.columns([1.3, 1.7])
        
        with col_metricas:
            m1, m2, m3 = str_visual.columns(3)
            m1.metric("Precio (USD)", p_usd)
            m2.metric("Precio (MXN)", p_mxn)
            m3.metric("Riesgo", riesgo)
            
            # Caja visual con las métricas de Darvas calculadas matemáticamente
            str_visual.markdown(f"""
            <div class="darvas-container">
                <div class="darvas-title">📦 Nicolas Darvas Box Strategy</div>
                <div style="font-size: 0.9em; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div><b>Techo Caja:</b> ${d_vals['techo']:.2f} USD</div>
                    <div><b>Suelo Caja:</b> ${d_vals['suelo']:.2f} USD</div>
                    <div style="color: #f87171; font-weight: bold;"><b>Stop Loss:</b> ${d_vals['stop_loss']:.2f} USD</div>
                    <div><b>Estado:</b> {d_vals['estado']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            str_visual.markdown("<br>**🤖 Evaluación Financiera del Comité:**", unsafe_allow_html=True)
            str_visual.write(analisis_completo)
            
        with col_grafico:
            if not historial_30d.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=historial_30d.index, 
                    y=historial_30d['Close'], 
                    mode='lines',
                    fill='tozeroy',  
                    fillcolor='rgba(37, 99, 235, 0.06)',
                    name='Cierre (USD)',
                    line=dict(color='#2563eb', width=2.5, shape='spline')
                ))
                
                # Dibujamos las líneas de Techo y Suelo de la Caja de Darvas directamente sobre el gráfico Plotly
                fig.add_hline(y=d_vals['techo'], line_dash="dash", line_color="#10b981", annotation_text="Techo Darvas")
                fig.add_hline(y=d_vals['suelo'], line_dash="dash", line_color="#ef4444", annotation_text="Suelo / Stop")
                
                fig.update_layout(
                    height=240, # Un poco de espacio para ver las líneas de Darvas claramente
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(226, 232, 240, 0.4)', side='right'),
                )
                str_visual.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                
                # --- NUEVA SECCIÓN: INTERPRETACIÓN DE LA GRÁFICA ---
                with str_visual.container(border=True):
                    # Pequeño resumen de datos técnicos duros
                    t1, t2, t3 = str_visual.columns(3)
                    t1.caption(f"📉 **Mínimo 30d:** ${tech['min']:.2f} USD")
                    t2.caption(f"📈 **Máximo 30d:** ${tech['max']:.2f} USD")
                    
                    color_rendimiento = "green" if tech['rendimiento'] >= 0 else "red"
                    t3.markdown(f"<p style='font-size:12px; margin:0; text-align:right;'><strong>Rendimiento mensual:</strong> <span style='color:{color_rendimiento}; font-weight:bold;'>{tech['rendimiento']:.2f}%</span></p>", unsafe_allow_html=True)
                    
                    # Llamada a la IA para interpretar el canal visual
                    interpretacion_grafica = interpretar_grafica_ia(simbolo, tech['max'], tech['min'], tech['actual'], tech['rendimiento'])
                    str_visual.markdown(f"📊 **Lectura Técnica de la Gráfica:** *{interpretacion_grafica}*")
            else:
                str_visual.warning("Historial de precios no disponible temporalmente.")

    analisis_html = analisis_completo.replace('\n', '<br>')
    html_bloques_activos += f"""
    <div style="background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0; border-radius: 0 5px 5px 0;">
        <div style="font-size: 18px; font-weight: bold; color: #1e293b;">🎯 {simbolo} — Precio: {p_usd} | {p_mxn}</div>
        <div style="font-size: 13px; color: #475569; margin: 5px 0; padding: 5px; background: #e2e8f0; border-radius: 4px;">
            <strong>[Caja de Darvas]</strong> Techo: ${d_vals['techo']:.2f} USD | Suelo: ${d_vals['suelo']:.2f} USD | 
            <span style="color:#dc2626;"><strong>Stop Loss sugerido: ${d_vals['stop_loss']:.2f} USD</strong></span> | Estado: {d_vals['estado']}
        </div>
        <p>{analisis_html}</p>
    </div>
    """

# --- SECCIÓN DE ENVÍO DE CORREO EN SIDEBAR ---
str_visual.sidebar.markdown("### ✉️ Exportación de Datos")
if str_visual.sidebar.button("Enviar Alerta de Inversión al Correo", use_container_width=True):
    # El correo electrónico ahora cuenta con una tabla de Darvas adjunta
    html_correo_completo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="background-color: #0f172a; color: white; padding: 20px; border-radius: 5px;">
            <h2>📊 Alerta de Inversión: Comité Buffett-Aschenbrenner (Con Caja de Darvas)</h2>
            <p>Reporte Diario Automatizado de Infraestructura de Cómputo y Semiconductores (TC: ${tipo_cambio_mxn:.2f} MXN)</p>
        </div>
        <h3>🌐 Panorama Macroeconómico Diario</h3>
        <table style="width:100%; border-collapse:collapse;">
            <tr>
                <td style="width:50%; padding:10px; background-color:#eff6ff; border:1px solid #ddd;"><strong>Noticia 1:</strong> {n1}</td>
                <td style="width:50%; padding:10px; background-color:#f8fafc; border:1px solid #ddd;"><strong>Noticia 2:</strong> {n2}</td>
            </tr>
            <tr>
                <td style="width:50%; padding:10px; background-color:#f8fafc; border:1px solid #ddd;"><strong>Noticia 3:</strong> {n3}</td>
                <td style="width:50%; padding:10px; background-color:#eff6ff; border:1px solid #ddd;"><strong>Noticia 4:</strong> {n4}</td>
            </tr>
        </table>
        <p style="background-color:#d1fae5; padding:10px; border-radius:5px;"><strong>Consejo del Comité:</strong> {consejo_global}</p>
        <h3>💡 Análisis Detallado por Activo</h3>
        {html_bloques_activos}
        <br>
        <h3>📋 Tabla de Resumen Diario</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 25px;">
            <thead>
                <tr style="background-color: #1e293b; color: white;">
                    <th style="padding: 12px; text-align: left;">Ticker</th>
                    <th style="padding: 12px; text-align: left;">Precio USD</th>
                    <th style="padding: 12px; text-align: left;">Precio MXN</th>
                    <th style="padding: 12px; text-align: left;">Recomendación Comité</th>
                    <th style="padding: 12px; text-align: left;">Nivel de Riesgo</th>
                </tr>
            </thead>
            <tbody>
    """
    for item in lista_resumen:
        color_fondo = "#fef3c7" if "RETENER" in item['Recomendación'] else ("#d1fae5" if "COMPRA" in item['Recomendación'] else "#fee2e2")
        html_correo_completo += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #ddd;"><strong>{item['Ticker']}</strong></td>
                    <td style="padding: 12px; border-bottom: 1px solid #ddd;">{item['Precio USD']}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #ddd;">{item['Precio MXN']}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #ddd; background-color: {color_fondo}; font-weight: bold;">{item['Recomendación']}</td>
                    <td style="padding: 12px; border-bottom: 1px solid #ddd;">{item['Nivel de Riesgo']}</td>
                </tr>
        """
    html_correo_completo += """
            </tbody>
        </table>
        <br>
        <p style='color: #64748b; font-size: 12px;'>Este informe fue estructurado dinámicamente utilizando SisFin Engine en Streamlit.</p>
    </body>
    </html>
    """
    
    with str_visual.sidebar.spinner("Despachando correo electrónico..."):
        exito = enviar_correo_html("📊 Reporte Avanzado SisFin: Matriz de Noticias e Inversiones (USD/MXN)", html_correo_completo)
        if exito:
            str_visual.sidebar.success("✉️ ¡Reporte enviado con éxito al correo!")
