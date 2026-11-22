using MySql.Data.MySqlClient;
using SonrisaDerrisa.Entidades;

namespace SonrisaDerrisa.Datos;

public static class DentistaDatos
{
    private const string Select = @"
        SELECT d.id_dentista, d.nombre, d.apellidos, d.cedula, d.telefono, d.id_especialidad,
               e.nombre AS especialidad,
               (SELECT COUNT(*) FROM cita c WHERE c.id_dentista = d.id_dentista) AS citas
        FROM dentista d
        JOIN especialidad e ON e.id_especialidad = d.id_especialidad";

    private static Dentista Mapear(MySqlDataReader dr) => new()
    {
        IdDentista = dr.GetInt32("id_dentista"),
        Nombre = dr.GetString("nombre"),
        Apellidos = dr.GetString("apellidos"),
        Cedula = dr.GetString("cedula"),
        Telefono = Conexion.Texto(dr, "telefono"),
        IdEspecialidad = dr.GetInt32("id_especialidad"),
        Especialidad = dr.GetString("especialidad"),
        Citas = dr.GetInt32("citas")
    };

    public static List<Dentista> Buscar(string? texto, int idEspecialidad) =>
        Conexion.Consultar(Select + @"
            WHERE (@t IS NULL OR CONCAT(d.nombre, ' ', d.apellidos, ' ', d.cedula) LIKE CONCAT('%', @t, '%'))
              AND (@e = 0 OR d.id_especialidad = @e)
            ORDER BY d.apellidos, d.nombre", Mapear,
            ("@t", string.IsNullOrWhiteSpace(texto) ? null : texto.Trim()), ("@e", idEspecialidad));

    public static Dentista? Obtener(int id) =>
        Conexion.Consultar(Select + " WHERE d.id_dentista = @id", Mapear, ("@id", id)).FirstOrDefault();

    public static void Guardar(Dentista d)
    {
        var datos = new (string, object?)[]
        {
            ("@id", d.IdDentista), ("@nombre", d.Nombre.Trim()), ("@apellidos", d.Apellidos.Trim()),
            ("@cedula", d.Cedula.Trim().ToUpper()),
            ("@tel", string.IsNullOrWhiteSpace(d.Telefono) ? null : d.Telefono.Trim()), ("@esp", d.IdEspecialidad)
        };
        Conexion.Ejecutar(d.IdDentista == 0
            ? "INSERT INTO dentista (nombre, apellidos, cedula, telefono, id_especialidad) VALUES (@nombre, @apellidos, @cedula, @tel, @esp)"
            : "UPDATE dentista SET nombre=@nombre, apellidos=@apellidos, cedula=@cedula, telefono=@tel, id_especialidad=@esp WHERE id_dentista=@id",
            datos);
    }

    public static void Eliminar(int id) =>
        Conexion.Ejecutar("DELETE FROM dentista WHERE id_dentista = @id", ("@id", id));

    public static List<Opcion> Opciones() =>
        Conexion.Consultar("SELECT id_dentista, CONCAT(nombre, ' ', apellidos) AS n FROM dentista ORDER BY n",
            dr => new Opcion { Id = dr.GetInt32(0), Texto = dr.GetString(1) });

    public static List<Opcion> Especialidades() =>
        Conexion.Consultar("SELECT id_especialidad, nombre FROM especialidad ORDER BY nombre",
            dr => new Opcion { Id = dr.GetInt32(0), Texto = dr.GetString(1) });
}
