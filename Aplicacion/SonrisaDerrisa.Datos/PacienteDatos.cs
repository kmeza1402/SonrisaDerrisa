using MySql.Data.MySqlClient;
using SonrisaDerrisa.Entidades;

namespace SonrisaDerrisa.Datos;

public static class PacienteDatos
{
    private const string Select = @"
        SELECT p.id_paciente, p.nombre, p.apellidos, p.fecha_nacimiento, p.telefono, p.correo,
               p.fecha_registro, h.id_historial, h.alergias, h.enfermedades, h.medicamentos
        FROM paciente p
        LEFT JOIN historial_clinico h ON h.id_paciente = p.id_paciente";

    private static Paciente Mapear(MySqlDataReader dr) => new()
    {
        IdPaciente = dr.GetInt32("id_paciente"),
        Nombre = dr.GetString("nombre"),
        Apellidos = dr.GetString("apellidos"),
        FechaNacimiento = dr.IsDBNull(dr.GetOrdinal("fecha_nacimiento")) ? null : dr.GetDateTime("fecha_nacimiento"),
        Telefono = dr.GetString("telefono"),
        Correo = Conexion.Texto(dr, "correo"),
        FechaRegistro = dr.GetDateTime("fecha_registro"),
        TieneHistorial = !dr.IsDBNull(dr.GetOrdinal("id_historial")),
        Alergias = Conexion.Texto(dr, "alergias"),
        Enfermedades = Conexion.Texto(dr, "enfermedades"),
        Medicamentos = Conexion.Texto(dr, "medicamentos")
    };

    public static List<Paciente> Buscar(string? texto) =>
        Conexion.Consultar(Select + @"
            WHERE @t IS NULL OR CONCAT(p.nombre, ' ', p.apellidos) LIKE CONCAT('%', @t, '%') OR p.telefono LIKE CONCAT('%', @t, '%')
            ORDER BY p.apellidos, p.nombre", Mapear, ("@t", string.IsNullOrWhiteSpace(texto) ? null : texto.Trim()));

    public static Paciente? Obtener(int id) =>
        Conexion.Consultar(Select + " WHERE p.id_paciente = @id", Mapear, ("@id", id)).FirstOrDefault();

    /// <summary>Guarda paciente e historial clínico en una sola transacción (dos tablas).</summary>
    public static void Guardar(Paciente p)
    {
        using var cn = Conexion.Abrir();
        using var tx = cn.BeginTransaction();
        try
        {
            var datos = new (string, object?)[]
            {
                ("@id", p.IdPaciente), ("@nombre", p.Nombre.Trim()), ("@apellidos", p.Apellidos.Trim()),
                ("@nac", p.FechaNacimiento), ("@tel", p.Telefono.Trim()),
                ("@correo", Vacio(p.Correo))
            };
            if (p.IdPaciente == 0)
            {
                using var ins = Conexion.Comando(cn, @"INSERT INTO paciente (nombre, apellidos, fecha_nacimiento, telefono, correo)
                    VALUES (@nombre, @apellidos, @nac, @tel, @correo)", datos);
                ins.Transaction = tx;
                ins.ExecuteNonQuery();
                p.IdPaciente = (int)ins.LastInsertedId;
            }
            else
            {
                using var upd = Conexion.Comando(cn, @"UPDATE paciente SET nombre=@nombre, apellidos=@apellidos,
                    fecha_nacimiento=@nac, telefono=@tel, correo=@correo WHERE id_paciente=@id", datos);
                upd.Transaction = tx;
                upd.ExecuteNonQuery();
            }

            using var hist = Conexion.Comando(cn, @"
                INSERT INTO historial_clinico (id_paciente, alergias, enfermedades, medicamentos)
                VALUES (@id, @a, @e, @m)
                ON DUPLICATE KEY UPDATE alergias=@a, enfermedades=@e, medicamentos=@m, fecha_actualizacion=CURRENT_DATE",
                ("@id", p.IdPaciente), ("@a", Vacio(p.Alergias)), ("@e", Vacio(p.Enfermedades)), ("@m", Vacio(p.Medicamentos)));
            hist.Transaction = tx;
            hist.ExecuteNonQuery();

            tx.Commit();
        }
        catch
        {
            tx.Rollback();
            throw;
        }
    }

    public static void Eliminar(int id) =>
        Conexion.Ejecutar("DELETE FROM paciente WHERE id_paciente = @id", ("@id", id));

    public static List<Opcion> Opciones() =>
        Conexion.Consultar("SELECT id_paciente, CONCAT(nombre, ' ', apellidos) AS n FROM paciente ORDER BY n",
            dr => new Opcion { Id = dr.GetInt32(0), Texto = dr.GetString(1) });

    private static string? Vacio(string? s) => string.IsNullOrWhiteSpace(s) ? null : s.Trim();
}
