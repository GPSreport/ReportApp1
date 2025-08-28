HTML pag

  HTML + Bootstrap + FontAwesome

  HTML define la estructura: mapa a la izquierda, estadísticas y fotos a la derecha.
  Bootstrap da diseño responsivo .
  FontAwesome provee íconos visuales.

Leaflet Map

  Crea el mapa centrado en Barranquilla.
  Usa OpenStreetMap como fuente de mapas.
  Agrupa todos los marcadores para facilitar su limpieza y actualización.

Actualización dinámica del mapa

  Limpia marcadores anteriores.
  Crea uno nuevo por cada reporte, con un popup que muestra información y foto.
  Ajusta automáticamente el zoom para mostrar todos los marcadores.

Estadísticas en tiempo real

  Muestra total de reportes, reportes de hoy y fecha del último reporte.
  Si no hay estadísticas desde el API, calcula algunas localmente.

Visualización de fotos

  Filtra reportes que tienen foto (foto_base64).
  Muestra solo las 5 más recientes.
  Permite verlas en grande en un modal (mostrarFotoModal).

Actualización automática

  Inicializa el mapa y carga datos al abrir la página.
  Actualiza todo cada 30 segundos sin recargar la página.
  Detecta si el usuario pierde conexión y avisa.
