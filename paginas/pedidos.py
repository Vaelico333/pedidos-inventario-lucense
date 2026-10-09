from typing import Any
import streamlit as st
from servicios.creador_pdf import generar_pdf_pedido
from datetime import datetime

class PaginaPedidos():
    
    @st.fragment(key="render_resumen_pedido")
    def render_resumen_pedido(proveedores: list):

        st.sidebar.header("📋 Pedido Actual")
        if st.session_state.pedido:
            if st.sidebar.button("🗑️ Borrar lista"):
                st.session_state.pedido.clear()
            col_txt, col_borrar = st.columns([1,1])
            prov_dict: dict[str, list] = dict.fromkeys(proveedores,[])
            for item, cantidad in list(st.session_state.pedido.items()):
                prov, pres, prod = item.split('-', 2)
                prov_dict[prov].append(f"✅ **{cantidad}x** {pres} de {prod}")
                with col_txt:
                    for p in prov_dict.keys():
                        [st.title(p) if prov_dict[p]]
                        [st.markdown(i) for i in prov_dict[p] if prov_dict[p]]
                with col_borrar:
                    if st.sidebar.button("✖️", key=f'btn_borrar_{prod}'):
                        st.session_state.pedido.pop(item)
                        st.rerun(scope="fragment")
            st.divider()
            datos_pdf = generar_pdf_pedido(st.session_state.pedido)
            fecha = datetime.now().strftime('%d/%m/%Y')
            st.sidebar.download_button("Generar PDF", data=datos_pdf, file_name=f"pedido_lucense_{fecha}.pdf", type="primary", key="btn_pdf", icon="📝")

        else:
            st.sidebar.info('Pedido vacío')    

    def llamada_agregar_producto(prov: str, producto: str, presentacion: str):

        cant_prod: float = st.session_state.get(f"cantidad_{prov}_{producto}", 0)
        id_item = f'{prov} - {presentacion} - {producto}'

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
        st.rerun(scope="render_resumen_pedido")

    def llamada_borrar_producto(prov: str, producto: str):

        id_item = f'{prov} - {producto}'
        if id_item in st.session_state.pedido:
            st.session_state.pedido.pop(id_item)
            st.toast(f'{producto} de {prov} retirado de la lista con éxito', icon="🗑️")
        st.rerun(scope="render_resumen_pedido")

    @st.fragment(key="pedidos")
    def pagina_pedidos(datos: dict[str, dict[str, dict[str, str] | str] | list[str] | str]):

        from servicios.mods import Modulares as mm
        prov = list(datos.keys())
        PaginaPedidos.render_resumen_pedido(prov)
        col_titulo, col_buscar = st.columns(2)
        with col_titulo:
            st.title("🛒 Hacer pedido")
        with col_buscar:
            col_input, col_btn = st.columns(2, vertical_alignment="center")
            with col_input:
                buscar = st.text_input(label="", placeholder="Introduce un producto", key="texto-buscar")
            with col_btn:
                btn_buscar = st.button("🔎 Buscar", key="btn-buscar")
        if btn_buscar:
            encontrado = False
            for prov, cats in datos.items():
                for cat, info in cats.items():
                    if isinstance(info, dict):
                        for prod, pres in info.items():
                            if buscar.lower() in prod.lower():
                                st.toast(f'{prod} encontrado')
                                encontrado += 1
                                mm.buscar(prov, prod, pres)
            if not encontrado:
                st.warning('Producto no encontrado')
            else:
                st.warning(f'Encontrados {encontrado} productos.')
        for prov in datos.keys():
            with st.expander(prov, key=f'expander_{prov}'):
                mm.render_bloque_proveedor(prov, datos[prov])

