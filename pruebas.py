import json
with open("./datos/proveedores.json", encoding="utf-8") as f:
    proveedores = json.load(f)

nuevo_json: dict[str | dict[dict]] = {}
for proveedor, value in proveedores.items():
    print(f'\n- Proveedor: {proveedor}')
    nuevo_json[proveedor] = dict()
    for campo, valor in value.items():
        print(f"\nCampo: {campo}")
        if ' : ' in valor[0]:
            nuevo_json[proveedor][campo] = dict()
            for producto in valor:
                prod, presentacion = producto.split(" : ")
                print(f'Producto: {prod}\nPresentación: {presentacion}')
                nuevo_json[proveedor][campo][prod] = presentacion
        else:
            print(f'Valores:\n{valor}')
            nuevo_json[proveedor] = dict()
            nuevo_json[proveedor][campo] = valor

for proveedor, value in nuevo_json.items():
    print(f'\n- Proveedor: {proveedor}')
    for campo, valor in value.items():
        print(f"\n· Campo: {campo}")
        if isinstance(valor, dict):
            for prod, presentacion in valor.items():
                print(f'· Producto: {prod}\n# Presentación: {presentacion}')
        else:
            print(f'# Valores:\n{valor}')
print(nuevo_json)

with open("./datos/datos_proveedores.json", '+w', encoding="utf-8") as f:
    proveedores: None = json.dump(nuevo_json, f, ensure_ascii=False)
