# Sonrisa Derrisa: Proyecto Final de Bases de Datos

Este es el sistema de citas, tratamientos y pagos para una clínica dental.

- **Equipo:** Bombones, grupo 952, UABC FIAD.
- **Integrantes:**
  - Meza Espinoza Kevin Andre [379140]
  - Zazueta Medrano Aidan [379479]
  - Jaime Mascareño Carlos Alberto [377175]
- **Profesora:** Julia Guadalupe Juárez Hernández

## Contenido

| Carpeta / archivo | Descripción |
|---|---|
| `Reporte.pdf` | Reporte técnico completo (etapas 1 a 7, álgebra relacional, SQL, aplicación, pruebas, incidencias y conclusiones) |
| `Sql/` | `01_esquema.sql`, `02_datos.sql`, `03_consultas_vistas.sql`, `04_rutinas.sql`, `05_pruebas.sql` |
| `Diagramas/` | DER en Crow's Foot, Chen, Connect to Columns, UML e IDEF1X (`.dot` editable + `.png` + `.pdf`) y `generar_diagramas.py` |
| `Aplicacion/` | Solución ASP.NET Core Razor Pages en capas (Web, Negocios, Datos, Entidades) |
| `Pruebas/` | `matriz_pruebas.csv`, capturas de cada caso y salidas reales de MySQL (`resultados_sql/`) |
| `Documentacion/generar_reporte.py` | Script que genera `Reporte.pdf` y la matriz de pruebas |

## Requisitos

- MySQL Server 8.0
- .NET SDK 10
- Python 3 con `reportlab`; solo hace falta para regenerar el reporte. Para regenerar los diagramas se necesita además Graphviz.

## 1. Crear la base de datos

Ejecuta los scripts en orden desde la carpeta `Sql`:

```powershell
cmd /c "mysql -u root -p --default-character-set=utf8mb4 < 01_esquema.sql"
cmd /c "mysql -u root -p --default-character-set=utf8mb4 < 02_datos.sql"
cmd /c "mysql -u root -p --default-character-set=utf8mb4 < 03_consultas_vistas.sql"
cmd /c "mysql -u root -p --default-character-set=utf8mb4 < 04_rutinas.sql"
```

Las pruebas de triggers, la función y los procedimientos incluyen casos que deben fallar, por eso se ejecutan con `--force`. Estas pruebas modifican datos. Para volver al estado inicial, vuelve a ejecutar los scripts 01 a 04.

```powershell
cmd /c "mysql -u root -p --force -vvv --default-character-set=utf8mb4 < 05_pruebas.sql"
```

## 2. Usuario de la aplicación (mínimo privilegio)

Crea el usuario en MySQL. Elige tu propia contraseña: no la guardes en el repositorio.

```sql
CREATE USER 'sonrisa_app'@'localhost' IDENTIFIED BY '<contraseña>';
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON sonrisa_derrisa.* TO 'sonrisa_app'@'localhost';
```

## 3. Ejecutar la aplicación

La cadena de conexión se guarda en User Secrets y no en `appsettings.json`.

```powershell
cd Aplicacion
dotnet user-secrets set "ConnectionStrings:SonrisaDerrisa" "Server=localhost;Database=sonrisa_derrisa;User ID=sonrisa_app;Password=<contraseña>;CharSet=utf8mb4;" --project SonrisaDerrisa.Web
dotnet run --project SonrisaDerrisa.Web
```

Después abre la URL que muestra la consola.

## Módulos

- **Pacientes:** alta, edición, búsqueda y eliminación. El historial clínico se guarda en la misma transacción.
- **Dentistas:** CRUD con especialidad y filtro.
- **Citas:** agenda con filtros sobre `vw_agenda`. Permite agendar, reprogramar y cancelar. Los triggers impiden empalmes y citas de pacientes sin historial.
- **Atender cita:** operación multitabla mediante `sp_atender_cita` (cita + detalle_cita + pago, todo o nada).
- **Registrar pago:** abonos limitados al saldo por el trigger `trg_pago_bi`.
- **Reporte de saldos:** sobre `vw_saldo_citas`, con totales y estado vacío.
