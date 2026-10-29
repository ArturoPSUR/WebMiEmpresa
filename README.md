# WebMiEmpresa
### Herramientas usadas:

Prompt Cowboy

Claude (Sonnet 5.5)

### Prompts usados:

**Primer Prompt:**

Quiero que actúes como un arquitecto de software full-stack con experiencia en proyectos educativos y containerización, y que me entregues una aplicación web completa, funcional y lista para ejecutar que cumpla los requisitos de una asignatura universitaria.

**Proyecto:** Una aplicación web orientada a una idea de negocio que recopila datos del centro educativo, su infraestructura y sus materiales. La aplicación debe permitir registrar y consultar los materiales e infraestructuras del centro (por ejemplo: nombre del elemento, tipo, ubicación, fecha de adquisición, vida útil estimada, estado y uso), de modo que sirva de base para analizar el uso del material y su vida útil, con el fin de optimizar y maximizar su utilidad, durabilidad y aprovechamiento. Puedes elegir los campos concretos que mejor representen este objetivo, manteniendo la aplicación sencilla.

**Requisitos obligatorios que debe cumplir la entrega:**

- **Frontend:** interfaz web sencilla y usable para listar, crear, editar y eliminar registros.
- **Backend:** API que gestione las operaciones CRUD y valide los datos recibidos.
- **Base de datos:** persistencia real de los registros (por ejemplo, SQLite o PostgreSQL), con un esquema claro.
- **Contenedor:** un `Dockerfile` (y un `docker-compose.yml` si hay varios servicios) que permita desplegar toda la aplicación con un solo comando.
- **CRUD básico:** operaciones de creación, lectura, actualización y eliminación completamente funcionales sobre al menos una entidad.

**Entregable esperado:** la estructura de carpetas y el código completo de cada archivo necesario, con las instrucciones exactas para construir y ejecutar el contenedor. Prioriza una solución mínima que funcione correctamente sobre una solución compleja; no añadas autenticación, pruebas avanzadas ni funcionalidades que no se hayan pedido, salvo que sean imprescindibles para que el CRUD funcione.

Antes de dar la solución, verifica que todos los archivos son coherentes entre sí (rutas, puertos, nombres de variables de entorno y dependencias) para que la aplicación arranque sin modificaciones.