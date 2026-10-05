import streamlit as st
from creador_pdf import generar_pdf_pedido
from datetime import datetime

class PaginaPedidos():
    @st.fragment(key="render_resumen_pedido")
    def render_resumen_pedido():
        st.sidebar.header("📋 Pedido Actual")
        if st.session_state.pedido:
            if st.button("🗑️ Borrar lista"):
                st.session_state.pedido.clear()
            col_txt, col_borrar = st.columns([4,1])
            for item, cantidad in list(st.session_state.pedido.items()):
                with col_txt:
                        st.sidebar.markdown(f"🔹 **{cantidad}x** {item}")
                with col_borrar:
                    if st.sidebar.button("✖️", key=f'btn_borrar_{item}'):
                        st.session_state.pedido.pop(item)
                        st.rerun(scope="fragment")
            st.divider()
            datos_pdf = generar_pdf_pedido(st.session_state.pedido)
            fecha = datetime.now().strftime('%d/%m/%Y')
            st.sidebar.download_button("Generar PDF", data=datos_pdf, file_name=f"pedido_lucense_{fecha}.pdf", type="primary", key="btn_pdf", icon="📝")

        else:
            st.sidebar.info('Pedido vacío')    

    def llamada_agregar_producto(prov: str, producto: str):
        cant_prod = st.session_state.get(f"cantidad_{prov}_{producto}", 0)
        id_item = f'{prov} - {producto}'

        cantidad_final = st.session_state.pedido.get(id_item, 0) + cant_prod
        if cantidad_final > 0:
            st.session_state.pedido[id_item] = st.session_state.pedido.get(id_item, 0) + cant_prod
            st.toast(f'{prov}: {cant_prod} x {producto} añadido al pedido', icon="➕")
        elif cantidad_final == 0:
            if id_item in st.session_state.pedido:
                st.session_state.pedido.pop(id_item)
                st.toast(f'{producto} de {prov} retirado de la lista por tener 0 unidades', icon="🗑️")
        else:
            st.warning("No se puede pedir menos de 0 productos")
        print(st.session_state.pedido)
        st.rerun(scope="render_resumen_pedido")

    def llamada_borrar_producto(prov: str, producto: str):
        id_item = f'{prov} - {producto}'
        if id_item in st.session_state.pedido:
            st.session_state.pedido.pop(id_item)
            st.toast(f'{producto} de {prov} retirado de la lista con éxito', icon="🗑️")
        st.rerun(scope="render_resumen_pedido")

    def producto_btn_cantidad(prov: str, producto: str):
        col_nombre, col_cantidad, col_btn = st.columns([2,1,1])

        with col_nombre:
            st.subheader(f'{producto}')
        with col_cantidad:
            st.number_input('Cantidad', step=1, on_change="ignore", key=f"cantidad_{prov}_{producto}",label_visibility='collapsed')
        with col_btn:
            st.button('Añadir al pedido', key=f'btn_{prov}_{producto}', use_container_width=True, on_click=PaginaPedidos.llamada_agregar_producto, args=(prov, producto))
            st.button('Borrar de la lista', key=f'btn_borrar_{prov}_{producto}', use_container_width=True, on_click=PaginaPedidos.llamada_borrar_producto, args=(prov, producto))
        "---"

    @st.fragment
    def render_bloque_proveedor(prov: str, datos_prov: dict):
        tlf = datos_prov['Teléfono']
        col_titulo, col_tlf = st.columns([1,2])
        if isinstance(tlf, str):
            with col_titulo:
                st.title(f'Teléfono:')
            with col_tlf:
                st.title(tlf)
        elif isinstance(tlf, list):
            with col_titulo:
                st.title(f'Teléfonos: ')
            with col_tlf:
                tlfs = ''
                for tele in tlf:
                    tlfs += f'{tele} '
                st.title(tlfs)
        "---"
        lista_productos = datos_prov['Productos']
        for prod in lista_productos:
            PaginaPedidos.producto_btn_cantidad(prov=prov, producto=prod)

        # Mostrar alertas pendientes si el callback las activó
        if "mensaje_toast" in st.session_state:
            st.toast(st.session_state.mensaje_toast)
            del st.session_state.mensaje_toast 
            
        if "mensaje_warning" in st.session_state:
            st.warning(st.session_state.mensaje_warning)
            del st.session_state.mensaje_warning


