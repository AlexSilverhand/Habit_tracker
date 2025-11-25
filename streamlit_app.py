import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de la API
API_BASE = "http://localhost:8000"

# Estilos CSS personalizados
st.markdown("""
<style>
    .habit-card {
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        background-color: #f9f9f9;
        margin: 0.5rem 0;
    }
    .completed-today {
        border-left-color: #4CAF50;
        background-color: #e8f5e8;
    }
    .missed {
        border-left-color: #f44336;
        background-color: #ffebee;
    }
    .inactive {
        border-left-color: #9e9e9e;
        background-color: #f5f5f5;
        opacity: 0.6;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def load_habits():
    """Cargar hábitos desde la API"""
    try:
        response = requests.get(f"{API_BASE}/habits")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        st.error("❌ No se pudo conectar con la API. Asegúrate de que el servidor esté ejecutándose.")
        return {}

def create_habit(name, description, goal_per_week):
    """Crear un nuevo hábito"""
    payload = {
        "name": name,
        "description": description,
        "goal_per_week": goal_per_week
    }
    response = requests.post(f"{API_BASE}/habit/create", json=payload)
    return response

def mark_habit_done(habit_id, day=None):
    """Marcar hábito como completado"""
    if day is None:
        day = datetime.now().strftime("%Y-%m-%d")
    
    payload = {
        "habit_id": habit_id,
        "day": day
    }
    response = requests.post(f"{API_BASE}/habit/done", json=payload)
    return response

def deactivate_habit(habit_id):
    """Desactivar hábito"""
    payload = {"habit_id": habit_id}
    response = requests.post(f"{API_BASE}/habit/deactivate", json=payload)
    return response

def get_week_dates():
    """Obtener fechas de la semana actual"""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    return [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def main():
    st.title("🎯 Habit Tracker")
    st.markdown("---")
    
    # Sidebar para crear nuevos hábitos
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        with st.expander("➕ Crear Nuevo Hábito", expanded=True):
            with st.form("create_habit_form"):
                name = st.text_input("Nombre del hábito*", placeholder="Ej: Ejercicio, Lectura...")
                description = st.text_area("Descripción", placeholder="Describe tu hábito...")
                goal_per_week = st.slider("Meta semanal", 1, 7, 3, 
                                         help="¿Cuántas veces por semana quieres hacer este hábito?")
                
                submitted = st.form_submit_button("🎯 Crear Hábito")
                if submitted:
                    if name.strip():
                        response = create_habit(name.strip(), description.strip(), goal_per_week)
                        if response.status_code == 200:
                            st.success("¡Hábito creado exitosamente!")
                            st.rerun()
                        else:
                            st.error("Error al crear el hábito")
                    else:
                        st.warning("Por favor ingresa un nombre para el hábito")
        
        st.markdown("---")
        st.header("📊 Estadísticas Rápidas")
        habits = load_habits()
        
        if habits:
            active_habits = [h for h in habits.values() if h["state"] != "Inactive"]
            total_completions = sum(len(h["completions"]) for h in active_habits)
            
            st.metric("Hábitos Activos", len(active_habits))
            st.metric("Completados Totales", total_completions)
            
            # Progreso semanal
            week_dates = get_week_dates()
            week_completions = sum(
                1 for h in active_habits 
                for completion in h["completions"] 
                if completion in week_dates
            )
            st.metric("Completados Esta Semana", week_completions)
    
    # Contenido principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📋 Mis Hábitos")
        
        habits = load_habits()
        
        if not habits:
            st.info("""
            👋 ¡Bienvenido a tu Habit Tracker!
            
            **Para comenzar:**
            1. Usa el panel lateral para crear tu primer hábito
            2. Establece una meta semanal realista
            3. ¡Marca tus progresos diarios!
            
            💡 **Tip:** Comienza con 1-2 hábitos y construye desde ahí.
            """)
        else:
            # Filtros
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                show_active = st.checkbox("Activos", value=True)
            with col_filter2:
                show_inactive = st.checkbox("Inactivos", value=False)
            with col_filter3:
                sort_by = st.selectbox("Ordenar por", ["Nombre", "Progreso", "Meta"])
            
            # Filtrar hábitos
            filtered_habits = []
            for habit_id, habit in habits.items():
                if (show_active and habit["state"] != "Inactive") or (show_inactive and habit["state"] == "Inactive"):
                    filtered_habits.append((habit_id, habit))
            
            # Ordenar
            if sort_by == "Nombre":
                filtered_habits.sort(key=lambda x: x[1]["name"])
            elif sort_by == "Progreso":
                filtered_habits.sort(key=lambda x: len(x[1]["completions"]), reverse=True)
            elif sort_by == "Meta":
                filtered_habits.sort(key=lambda x: x[1]["goal_per_week"], reverse=True)
            
            # Mostrar hábitos
            for habit_id, habit in filtered_habits:
                state_class = ""
                if habit["state"] == "Inactive":
                    state_class = "inactive"
                elif habit["state"] == "CompletedToday":
                    state_class = "completed-today"
                
                with st.container():
                    st.markdown(f'<div class="habit-card {state_class}">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.subheader(habit["name"])
                        if habit["description"]:
                            st.caption(habit["description"])
                        
                        # Progreso
                        completions = len(habit["completions"])
                        goal = habit["goal_per_week"]
                        progress = completions / goal if goal > 0 else 0
                        
                        st.progress(min(progress, 1.0))
                        st.caption(f"**{completions}/{goal}** completados esta semana")
                        
                        # Completados recientes
                        if habit["completions"]:
                            recent = sorted(habit["completions"], reverse=True)[:3]
                            st.caption(f"Últimos: {', '.join(recent)}")
                    
                    with col2:
                        if habit["state"] != "Inactive":
                            today = datetime.now().strftime("%Y-%m-%d")
                            already_done = today in habit["completions"]
                            
                            if already_done:
                                st.success("✅ Hoy")
                            else:
                                if st.button("🎯 Marcar Hoy", key=f"done_{habit_id}"):
                                    response = mark_habit_done(habit_id)
                                    if response.status_code == 200:
                                        st.rerun()
                                    else:
                                        st.error("Error al marcar como completado")
                    
                    with col3:
                        if habit["state"] != "Inactive":
                            if st.button("❌ Desactivar", key=f"deact_{habit_id}"):
                                response = deactivate_habit(habit_id)
                                if response.status_code == 200:
                                    st.rerun()
                                else:
                                    st.error("Error al desactivar")
                        else:
                            st.caption("Inactivo")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.header("📈 Análisis")
        
        if habits:
            active_habits = [h for h in habits.values() if h["state"] != "Inactive"]
            
            if active_habits:
                # Gráfico de progreso semanal
                st.subheader("Progreso Semanal")
                
                week_data = []
                week_dates = get_week_dates()
                
                for habit in active_habits:
                    week_completions = sum(1 for d in week_dates if d in habit["completions"])
                    week_data.append({
                        "Hábito": habit["name"],
                        "Completados": week_completions,
                        "Meta": habit["goal_per_week"],
                        "Progreso": min(week_completions / habit["goal_per_week"], 1.0) if habit["goal_per_week"] > 0 else 0
                    })
                
                if week_data:
                    df = pd.DataFrame(week_data)
                    
                    # Gráfico de barras
                    fig = px.bar(df, x="Hábito", y=["Completados", "Meta"], 
                                title="Progreso vs Meta Semanal",
                                barmode="group")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Métricas de rendimiento
                    st.subheader("🏆 Rendimiento")
                    
                    total_possible = sum(h["goal_per_week"] for h in active_habits)
                    total_actual = sum(len(h["completions"]) for h in active_habits if any(d in week_dates for d in h["completions"]))
                    
                    if total_possible > 0:
                        performance_rate = (total_actual / total_possible) * 100
                        
                        col_perf1, col_perf2 = st.columns(2)
                        with col_perf1:
                            st.metric("Tasa de Éxito", f"{performance_rate:.1f}%")
                        with col_perf2:
                            st.metric("Completados/Meta", f"{total_actual}/{total_possible}")
                        
                        # Mensaje motivacional
                        if performance_rate >= 80:
                            st.success("🎉 ¡Excelente trabajo! Sigue así.")
                        elif performance_rate >= 60:
                            st.info("💪 Buen progreso. ¡Tú puedes!")
                        else:
                            st.warning("🌟 Mañana es una nueva oportunidad.")
                
                # Hábitos más exitosos
                st.subheader("⭐ Top Hábitos")
                successful_habits = sorted(
                    [h for h in active_habits if h["goal_per_week"] > 0],
                    key=lambda x: len(x["completions"]) / x["goal_per_week"],
                    reverse=True
                )[:3]
                
                for i, habit in enumerate(successful_habits, 1):
                    rate = (len(habit["completions"]) / habit["goal_per_week"]) * 100
                    st.write(f"{i}. **{habit['name']}** - {rate:.1f}%")
            
            else:
                st.info("No hay hábitos activos para mostrar análisis.")
        
        st.markdown("---")
        st.header("💡 Consejos")
        st.info("""
        **Para mantener la constancia:**
        - 🎯 Empresa con metas pequeñas
        - 📅 Establece una rutina consistente
        - 🎉 Celebra tus progresos
        - 🔄 Revisa y ajusta tus metas
        """)

if __name__ == "__main__":
    main()