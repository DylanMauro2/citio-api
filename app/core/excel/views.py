from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .parser import parsear_excel


class ImportarExcelView(APIView):
    """
    Vista base para importar Excel. Subclasear y definir `mapeo`.
    Sobreescribir `validar(data, errores)` para agregar validaciones propias.
    """
    parser_classes = [MultiPartParser]
    mapeo = []

    def validar(self, data: list, errores: list) -> None:
        """
        Hook para validaciones de negocio específicas de cada entidad.
        Modificar `data` y `errores` en lugar.
        """
        pass

    def post(self, request):
        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'error': 'No se envió ningún archivo.'}, status=400)

        data, errores = parsear_excel(archivo, self.mapeo)
        self.validar(data, errores)

        return Response({
            'total_filas': len(data),
            'total_errores': len(errores),
            'valido': len(errores) == 0,
            'data': data,
            'errores': errores,
        })
