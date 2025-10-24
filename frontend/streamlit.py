import streamlit as st
import requests

API_BASE = "http://fastapi_app:8000"  

st.set_page_config(page_title="Chat con RAG", page_icon="💬", layout="centered")

# --- Estado global ---
if "token" not in st.session_state:
    st.session_state.token = None
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "chat_title" not in st.session_state:
    st.session_state.chat_title = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# AUTENTICACIÓN
def auth_page():
    st.title("🔐 Iniciar sesión o registrarse")

    tab_login, tab_register = st.tabs(["Iniciar sesión", "Registrarse"])

    # --- LOGIN ---
    with tab_login:
        username = st.text_input("Correo electrónico", key="login_email")
        password = st.text_input("Contraseña", type="password", key="login_pass")

        if st.button("Iniciar sesión", key="login_btn"):
            try:
                response = requests.post(
                    f"{API_BASE}/login",
                    data={"username": username, "password": password}
                )
                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["token"]
                    st.success("Inicio de sesión correcto ✅")
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

    # --- REGISTRO ---
    with tab_register:
        reg_email = st.text_input("Correo electrónico", key="reg_email")
        reg_password = st.text_input("Contraseña", type="password", key="reg_pass")

        if st.button("Crear cuenta", key="register_btn"):
            if not reg_email or not reg_password:
                st.warning("Por favor completa todos los campos")
            else:
                try:
                    resp = requests.post(
                        f"{API_BASE}/users/",
                        json={"email": reg_email, "password": reg_password}
                    )
                    if resp.status_code == 201:
                        st.success("Cuenta creada correctamente ✅. Ahora inicia sesión.")
                    elif resp.status_code == 409:
                        st.warning("Ya existe un usuario con ese correo.")
                    else:
                        st.error(f"Error {resp.status_code}: {resp.text}")
                except Exception as e:
                    st.error(f"Error al conectar con el backend: {e}")

# LISTA DE CHATS
def load_chats():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    r = requests.get(f"{API_BASE}/chats/", headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        st.error("Error al cargar chats")
        return []

def create_chat():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    if st.sidebar.button("Crear nuevo chat"):
        r = requests.post(
            f"{API_BASE}/chats/",
            headers=headers,
            json={"title": "Nuevo chat"}
        )
        if r.status_code == 201:
            new_chat = r.json()
            st.success("Chat creado ✅")

            st.session_state.chat_id = new_chat["id"]
            st.session_state.chat_title = new_chat["title"]
            st.session_state.messages = []

            st.rerun()
        else:
            st.error("Error al crear el chat")

def update_chat_title(chat_id, new_title):
    """Actualiza el título del chat"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    r = requests.put(
        f"{API_BASE}/chats/{chat_id}",
        headers=headers,
        json={"title": new_title}
    )
    if r.status_code == 200:
        st.success("Título actualizado ✅")
        st.session_state.chat_title = new_title
    else:
        st.error(f"Error al actualizar el título ({r.status_code})")

def delete_chat(chat_id):
    """Elimina completamente el chat"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    r = requests.delete(f"{API_BASE}/chats/{chat_id}", headers=headers)
    if r.status_code == 204:
        st.success("Chat eliminado ✅")
        st.session_state.chat_id = None
        st.session_state.chat_title = None
        st.session_state.messages = []
        st.rerun()
    else:
        st.error(f"Error al eliminar el chat ({r.status_code})")

def clear_chat(chat_id):
    """Elimina solo los mensajes del chat"""
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    r = requests.delete(f"{API_BASE}/chats/clear/{chat_id}", headers=headers)
    if r.status_code == 200 or r.status_code == 204:
        st.success("Mensajes eliminados ✅")
        st.session_state.messages = []
    else:
        st.error(f"Error al limpiar el chat ({r.status_code})")

# MENSAJES DE CHAT
def load_messages(chat_id):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    r = requests.get(f"{API_BASE}/messages/{chat_id}", headers=headers)
    if r.status_code == 200:
        return r.json()
    return []

def send_message(content):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        with requests.post(
            f"{API_BASE}/chats/talk/{st.session_state.chat_id}",
            json={"content": content},
            headers=headers,
            stream=True
        ) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                yield chunk
    except requests.exceptions.RequestException as e:
        st.error(f"Error al enviar mensaje: {e}")

# SUBIDA DE DOCUMENTOS
def upload_document():
    st.subheader("📄 Subir documento para contexto RAG")
    uploaded_file = st.file_uploader("Sube un archivo (.pdf, .txt o .docx)", type=["pdf", "txt", "docx"])
    if uploaded_file:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        with st.spinner("Procesando archivo..."):
            files = {"file": uploaded_file.getvalue()}
            r = requests.post(f"{API_BASE}/embeddings/upload/file", files={"file": uploaded_file}, headers=headers)
            if r.status_code == 200:
                st.success("✅ Documento subido correctamente")
            elif r.status_code == 409:
                st.warning(f"⚠️ {r.json().get('detail', 'El documento ya fue subido anteriormente.')}")
            else:
                st.error(f"Error {r.status_code}: {r.text}")

# APP PRINCIPAL
if not st.session_state.token:
    auth_page()
else:
    st.sidebar.title("Menú")
    chats = load_chats()

    # Lista de chats
    st.sidebar.subheader("💬 Tus Chats")

    for chat in chats:
        if st.sidebar.button(f"🗨️ {chat['title']}", key=f"chat_{chat['id']}"):
            st.session_state.chat_id = chat["id"]
            st.session_state.chat_title = chat["title"]
            st.session_state.messages = []  # limpiar historial local
            st.rerun()

    create_chat()
    st.sidebar.divider()

    # Si hay un chat seleccionado, mostrar acciones
    if st.session_state.chat_id:
        st.sidebar.markdown("### ⚙️ Opciones del chat")
        
        # Editar título
        new_title = st.sidebar.text_input("Editar título", value=st.session_state.chat_title or "")
        if st.sidebar.button("💾 Guardar título", key="sidebar_save_title"):
            if new_title.strip():
                update_chat_title(st.session_state.chat_id, new_title)

        # Limpiar mensajes
        if st.sidebar.button("🧹 Limpiar chat", key="sidebar_clear_chat"):
            clear_chat(st.session_state.chat_id)

        # Eliminar chat
        if st.sidebar.button("🗑️ Eliminar chat", key="sidebar_delete_chat"):
            delete_chat(st.session_state.chat_id)

        st.sidebar.divider()

    # Mostrar el chat seleccionado
    if st.session_state.chat_id:
        st.subheader(f"💬 Chat: {st.session_state.chat_title or 'Nuevo chat'}")

        # Cargar historial si no está en memoria
        if not st.session_state.messages:
            st.session_state.messages = load_messages(st.session_state.chat_id)

        # Mostrar los mensajes previos (persisten)
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg['content'])

        # Campo de entrada del usuario
        if user_input := st.chat_input("Tu pregunta:"):
            # Mostrar el mensaje del usuario inmediatamente
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)
            
            with st.chat_message("assistant"):
                placeholder = st.empty()                                                                                                                                                   
                placeholder.markdown("💭 Pensando...") 
                
                full_response = ""
                response_stream = send_message(user_input)

                for chunk in response_stream:                                                                                                                                              
                    full_response += chunk                                                                                                                                                 
                    placeholder.markdown(full_response) 

            if full_response:
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

        st.divider()
        upload_document()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.token = None
        st.rerun()
