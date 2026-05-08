from dataclasses import dataclass, field
from typing import Literal

TipoCampo = Literal['string', 'integer', 'decimal', 'date']


@dataclass
class ColumnaExcel:
    campo: str                    # nombre del campo en la salida JSON
    celda: str                    # celda del encabezado, ej: "A1" — define la columna
    tipo: TipoCampo               # tipo esperado del valor
    requerido: bool = True
    opciones: list | None = None  # valores válidos; None = sin restricción

    @property
    def columna(self) -> str:
        """Extrae la letra de columna desde la celda del encabezado."""
        import re
        return re.match(r'([A-Za-z]+)', self.celda).group(1).upper()

    @property
    def fila_encabezado(self) -> int:
        """Extrae el número de fila del encabezado."""
        import re
        return int(re.search(r'(\d+)', self.celda).group(1))

    def celda_en_fila(self, fila: int) -> str:
        return f"{self.columna}{fila}"
