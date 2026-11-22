using MySql.Data.MySqlClient;

namespace SonrisaDerrisa.Datos;

public static class Conexion
{
    private static string? _cadena;

    public static void Configurar(string cadena) => _cadena = cadena;

    public static MySqlConnection Abrir()
    {
        if (string.IsNullOrWhiteSpace(_cadena))
            throw new InvalidOperationException("No se configuró ConnectionStrings:SonrisaDerrisa (User Secrets).");
        var cn = new MySqlConnection(_cadena);
        cn.Open();
        return cn;
    }

    internal static MySqlCommand Comando(MySqlConnection cn, string sql, params (string, object?)[] parametros)
    {
        var cmd = new MySqlCommand(sql, cn);
        foreach (var (nombre, valor) in parametros)
            cmd.Parameters.AddWithValue(nombre, valor ?? DBNull.Value);
        return cmd;
    }

    public static int Ejecutar(string sql, params (string, object?)[] parametros)
    {
        using var cn = Abrir();
        using var cmd = Comando(cn, sql, parametros);
        return cmd.ExecuteNonQuery();
    }

    public static List<T> Consultar<T>(string sql, Func<MySqlDataReader, T> mapear, params (string, object?)[] parametros)
    {
        using var cn = Abrir();
        using var cmd = Comando(cn, sql, parametros);
        using var dr = cmd.ExecuteReader();
        var lista = new List<T>();
        while (dr.Read()) lista.Add(mapear(dr));
        return lista;
    }

    public static object? Escalar(string sql, params (string, object?)[] parametros)
    {
        using var cn = Abrir();
        using var cmd = Comando(cn, sql, parametros);
        return cmd.ExecuteScalar();
    }

    internal static string? Texto(MySqlDataReader dr, string col) =>
        dr.IsDBNull(dr.GetOrdinal(col)) ? null : dr.GetString(col);
}
