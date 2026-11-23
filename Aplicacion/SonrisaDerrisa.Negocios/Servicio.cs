using MySql.Data.MySqlClient;
using SonrisaDerrisa.Datos;

namespace SonrisaDerrisa.Negocios;

/// <summary>Error de regla de negocio con un mensaje apto para el usuario.</summary>
public class ReglaNegocioException(string mensaje) : Exception(mensaje);

public static class Servicio
{
    public static void Configurar(string cadena) => Conexion.Configurar(cadena);

    /// <summary>Ejecuta una operación de datos y traduce los errores de MySQL a mensajes claros.</summary>
    public static T Ejecutar<T>(Func<T> operacion)
    {
        try { return operacion(); }
        catch (MySqlException ex)
        {
            // Bitácora técnica en consola; al usuario sólo se le muestra el mensaje traducido.
            Console.Error.WriteLine($"[MySQL {ex.Number}] {ex.Message}");
            throw new ReglaNegocioException(Traducir(ex));
        }
    }

    public static void Ejecutar(Action operacion) => Ejecutar(() => { operacion(); return 0; });

    private static string Traducir(MySqlException ex) => ex.Number switch
    {
        1644 => ex.Message, // SIGNAL de trigger o procedimiento (mensaje ya redactado en la BD)
        1062 when ex.Message.Contains("cedula") => "Ya existe un dentista con esa cédula.",
        1062 when ex.Message.Contains("correo") => "Ya existe un paciente con ese correo.",
        1062 => "El registro ya existe.",
        // 1217 es lo que recibe el usuario de mínimos privilegios (no ve el detalle de la FK); root recibe 1451.
        1451 or 1217 =>"No se puede eliminar porque tiene citas u otros registros relacionados.",
        1452 => "El registro relacionado no existe.",
        3819 when ex.Message.Contains("diente") => "El diente debe tener formato FDI de dos dígitos (11 a 88).",
        3819 when ex.Message.Contains("telefono") => "El teléfono debe tener 10 dígitos.",
        3819 when ex.Message.Contains("monto") => "El monto debe ser mayor a cero.",
        3819 => "Los datos no cumplen las reglas de la base de datos.",
        0 or 1042 or 1045 => "No fue posible conectar con la base de datos.",
        _ => "Ocurrió un error en la base de datos. Intente de nuevo."
    };
}
