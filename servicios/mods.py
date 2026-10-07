import streamlit as st

class Modulares():
    def producto_btn_cantidad(prov: str, producto: str, presentacion: str, inventario: bool=False):

        from paginas.pedidos import PaginaPedidos as pp
        col_nombre, col_cantidad, col_btn = st.columns([2,1,1], vertical_alignment="center")

        with col_nombre:
            st.subheader(f'{producto}')
            st.markdown(f'**{presentacion}**')
        with col_cantidad:
            st.number_input('Cantidad', step=0.01, on_change="ignore", key=f"cantidad_{prov}_{producto}",label_visibility='collapsed')
        with col_btn:
            if not inventario:
                st.button('Añadir al pedido', key=f'btn_{prov}_{producto}', use_container_width=True, on_click=pp.llamada_agregar_producto, args=(prov, producto, presentacion))
                st.button('Borrar de la lista', key=f'btn_borrar_{prov}_{producto}', use_container_width=True, on_click=pp.llamada_borrar_producto, args=(prov, producto))
            else:
                # Implementar lógica de inventario
                pass
        "---"

    @st.fragment
    def render_bloque_proveedor(prov: str, datos_prov: dict[str, dict[str, str] | str] | list[str]):
        tlf: str | list = datos_prov['Teléfono']
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
        lista_productos: dict[str, str] = datos_prov['Productos']
        for prod, presentacion in lista_productos.items():
            Modulares.producto_btn_cantidad(prov=prov, producto=prod, presentacion=presentacion)

        # Mostrar alertas pendientes si el callback las activó
        if "mensaje_toast" in st.session_state:
            st.toast(st.session_state.mensaje_toast)
            del st.session_state.mensaje_toast 
            
        if "mensaje_warning" in st.session_state:
            st.warning(st.session_state.mensaje_warning)
            del st.session_state.mensaje_warning
        
        def buscar():
            pass

