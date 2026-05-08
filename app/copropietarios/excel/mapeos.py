from core.excel.mapping import ColumnaExcel

MAPEO_UNIDADES = [
    ColumnaExcel(campo='condominio_id',  celda='A1', tipo='integer'),
    ColumnaExcel(campo='numero',         celda='B1', tipo='string'),
    ColumnaExcel(campo='tipo',           celda='C1', tipo='string'),
    ColumnaExcel(campo='piso',           celda='D1', tipo='string',  requerido=False),
    ColumnaExcel(campo='block',          celda='E1', tipo='string',  requerido=False),
    ColumnaExcel(campo='rol_sii',        celda='F1', tipo='string',  requerido=False),
    ColumnaExcel(campo='alicuota',       celda='G1', tipo='decimal', requerido=False),
    ColumnaExcel(campo='superficie_m2',  celda='H1', tipo='decimal', requerido=False),
]
