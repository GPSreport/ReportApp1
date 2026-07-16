# Arquitectura Base Frontend

## Objetivo
Mantener una separacion limpia entre presentacion, logica, datos y utilidades.

## Estructura
- src/app: rutas y composicion de paginas (App Router)
- src/components: componentes visuales (presentacion)
- src/hooks: logica de estado y flujo de interfaz
- src/services: acceso a datos externos (API, adapters)
- src/lib: utilidades puras y helpers compartidos
- src/providers: providers globales de React
- src/types: tipos y contratos TypeScript
- src/styles: estilos globales y temas

## Regla principal
Los componentes visuales en src/components no deben contener logica de negocio ni acceso directo a API.

## Flujo recomendado
1. app/page.tsx compone la pantalla.
2. hooks resuelven la logica de UI.
3. services resuelven acceso a datos.
4. lib encapsula utilidades reutilizables.
5. components solo renderizan props.
