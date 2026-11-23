using System.Data;
using MySql.Data.MySqlClient;
using SonrisaDerrisa.Entidades;

namespace SonrisaDerrisa.Datos;

public static class CitaDatos
{
    /// <summary>Agenda desde la vista vw_agenda con filtros opcionales.</summary>
    public static List<AgendaItem> Agenda(DateTime? desde, DateTime? hasta, int idDentista, string? estado, string? paciente) =>
        Conexion.Consultar(@"
            SELECT * FROM vw_agenda
            WHERE (@desde IS NULL OR fecha >= @desde) AND (@hasta IS NULL OR fecha <= @hasta)
              AND (@d = 0 OR id_dentista = @d) AND (@e IS NULL OR estado = @e)
              AND (@p IS NULL OR paciente LIKE CONCAT('%', @p, '%'))
            ORDER BY fecha DESC, hora", dr => new AgendaItem
        {
            IdCita = dr.GetInt32("id_cita"),
            Fecha = dr.GetDateTime("fecha"),
            Hora = dr.GetTimeSpan("hora"),
            Estado = dr.GetString("estado"),
            Motivo = Conexion.Texto(dr, "motivo"),
            IdPaciente = dr.GetInt32("id_paciente"),
            Paciente = dr.GetString("paciente"),
            Telefono = dr.GetString("telefono"),
            IdDentista = dr.GetInt32("id_dentista"),
            Dentista = dr.GetString("dentista"),
            Especialidad = dr.GetString("especialidad"),
            Alergias = Conexion.Texto(dr, "alergias")
        },
        ("@desde", desde), ("@hasta", hasta), ("@d", idDentista),
        ("@e", string.IsNullOrWhiteSpace(estado) ? null : estado),
        ("@p", string.IsNullOrWhiteSpace(paciente) ? null : paciente.Trim()));

    public static Cita? Obtener(int id) =>
        Conexion.Consultar("SELECT * FROM cita WHERE id_cita = @id", dr => new Cita
        {
            IdCita = dr.GetInt32("id_cita"),
            IdPaciente = dr.GetInt32("id_paciente"),
            IdDentista = dr.GetInt32("id_dentista"),
            Fecha = dr.GetDateTime("fecha"),
            Hora = dr.GetTimeSpan("hora"),
            Motivo = Conexion.Texto(dr, "motivo"),
            Estado = dr.GetString("estado")
        }, ("@id", id)).FirstOrDefault();

    /// <summary>Alta o reprogramación. Los triggers validan RN2 y RN5.</summary>
    public static void Guardar(Cita c)
    {
        var datos = new (string, object?)[]
        {
            ("@id", c.IdCita), ("@p", c.IdPaciente), ("@d", c.IdDentista), ("@f", c.Fecha!.Value.Date),
            ("@h", c.Hora), ("@m", string.IsNullOrWhiteSpace(c.Motivo) ? null : c.Motivo.Trim())
        };
        Conexion.Ejecutar(c.IdCita == 0
            ? "INSERT INTO cita (id_paciente, id_dentista, fecha, hora, motivo) VALUES (@p, @d, @f, @h, @m)"
            : "UPDATE cita SET id_paciente=@p, id_dentista=@d, fecha=@f, hora=@h, motivo=@m WHERE id_cita=@id",
            datos);
    }

    public static int Cancelar(int id) =>
        Conexion.Ejecutar("UPDATE cita SET estado = 'Cancelada' WHERE id_cita = @id AND estado = 'Programada'", ("@id", id));

    /// <summary>Operación transaccional multitabla: procedimiento sp_atender_cita.</summary>
    public static void Atender(int idCita, int idTratamiento, string? diente, decimal? precio, decimal? monto, string? metodo)
    {
        using var cn = Conexion.Abrir();
        using var cmd = Conexion.Comando(cn, "sp_atender_cita",
            ("p_id_cita", idCita), ("p_id_tratamiento", idTratamiento), ("p_diente", diente),
            ("p_precio", precio), ("p_monto_pago", monto), ("p_metodo_pago", metodo));
        cmd.CommandType = CommandType.StoredProcedure;
        cmd.ExecuteNonQuery();
    }

    public static void RegistrarPago(int idCita, decimal monto, string metodo) =>
        Conexion.Ejecutar("INSERT INTO pago (id_cita, monto, metodo_pago) VALUES (@c, @m, @mp)",
            ("@c", idCita), ("@m", monto), ("@mp", metodo));

    public static decimal Saldo(int idCita) =>
        Convert.ToDecimal(Conexion.Escalar("SELECT fn_saldo_cita(@c)", ("@c", idCita)));

    public static List<Opcion> Tratamientos() =>
        Conexion.Consultar("SELECT id_tratamiento, nombre, precio_base FROM tratamiento ORDER BY nombre",
            dr => new Opcion { Id = dr.GetInt32(0), Texto = dr.GetString(1), Precio = dr.GetDecimal(2) });

    /// <summary>Reporte de saldos desde la vista vw_saldo_citas.</summary>
    public static List<SaldoCita> Saldos(string? paciente, bool soloPendientes) =>
        Conexion.Consultar(@"
            SELECT * FROM vw_saldo_citas
            WHERE (@p IS NULL OR paciente LIKE CONCAT('%', @p, '%')) AND (@s = 0 OR saldo > 0)
            ORDER BY saldo DESC, fecha", dr => new SaldoCita
        {
            IdCita = dr.GetInt32("id_cita"),
            Fecha = dr.GetDateTime("fecha"),
            IdPaciente = dr.GetInt32("id_paciente"),
            Paciente = dr.GetString("paciente"),
            Dentista = dr.GetString("dentista"),
            Total = dr.GetDecimal("total"),
            Pagado = dr.GetDecimal("pagado"),
            Saldo = dr.GetDecimal("saldo")
        }, ("@p", string.IsNullOrWhiteSpace(paciente) ? null : paciente.Trim()), ("@s", soloPendientes ? 1 : 0));

    public static List<(string Nombre, int Total)> Conteos() =>
        Conexion.Consultar(@"
            SELECT 'Pacientes', COUNT(*) FROM paciente UNION ALL
            SELECT 'Dentistas', COUNT(*) FROM dentista UNION ALL
            SELECT 'Citas programadas', COUNT(*) FROM cita WHERE estado = 'Programada' UNION ALL
            SELECT 'Citas con saldo', COUNT(*) FROM vw_saldo_citas WHERE saldo > 0",
            dr => (dr.GetString(0), dr.GetInt32(1)));
}
