import streamlit as st

def producto_btn_cantidad(prov: str, producto: str, presentacion: str, inventario: bool=False, buscar=""):
    "Genera un bloque que contiene el nombre del producto, su presentación, un input de cantidad y un botón para añadirlo."
    from pages.pedidos import llamada_agregar_producto
    col_nombre, col_cantidad, col_btn = st.columns([2,1,1], vertical_alignment="center")

    with col_nombre:
        st.subheader(f'{producto}')
        st.markdown(f'**{presentacion}**')
    with col_cantidad:
        st.number_input('Cantidad', step=0.01, on_change="ignore", key=f"cantidad_{prov}_{producto}",label_visibility='collapsed')
    with col_btn:
        if not inventario:
            st.button('Añadir al pedido', key=f'{buscar}_btn_{prov}_{producto}', use_container_width=True, on_click=llamada_agregar_producto, args=(prov, producto, presentacion))
        else:
            # Implementar lógica de inventario
            pass
    st.divider()

@st.fragment
def render_bloque_proveedor(prov: str, datos_prov: dict[str, dict[str, str] | str] | list[str]):
    "Crea un bloque para cada proveedor con su teléfono y la lista de productos"
    tlf: str | list = datos_prov['Teléfono']
    if isinstance(tlf, str):
        st.caption(f'Teléfono: {tlf}')
    elif isinstance(tlf, list):
        tlfs = ''
        for tele in tlf:
            tlfs += f'{tele} '
        st.caption(f'Teléfonos: {tlfs}')

    st.divider()

    lista_productos: dict[str, str] = datos_prov['Productos']
    for prod, presentacion in lista_productos.items():
        producto_btn_cantidad(prov=prov, producto=prod, presentacion=presentacion)

    # Mostrar alertas pendientes si el callback las activó
    if "mensaje_toast" in st.session_state:
        st.toast(st.session_state.mensaje_toast)
        del st.session_state.mensaje_toast 
        
    if "mensaje_warning" in st.session_state:
        st.warning(st.session_state.mensaje_warning)
        del st.session_state.mensaje_warning
    
def busqueda(prov, producto, presentacion, inventario =False):
    "Busca entre los productos disponibles."
    col_nombre, col_cantidad, col_btn = st.columns([2,1,1], vertical_alignment="center")
    if not inventario:
        producto_btn_cantidad(prov, producto, presentacion, inventario=False, buscar="buscar")
    else:
        producto_btn_cantidad(prov, producto, presentacion, inventario=True, buscar="buscar_inv")
        # Implementar lógica de inventario
        pass
    st.divider()
