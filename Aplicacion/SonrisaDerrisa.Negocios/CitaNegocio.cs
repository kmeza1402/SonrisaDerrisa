using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;

namespace SonrisaDerrisa.Negocios;

/// <summary>Validaciones de aplicación previas a las reglas que hace cumplir la BD.</summary>
public static class CitaNegocio
{
    public static readonly string[] Metodos = ["Efectivo", "Tarjeta", "Transferencia"];

    public static void Guardar(Cita c)
    {
        if (c.IdCita == 0 && c.Fecha!.Value.Date < DateTime.Today)
            throw new ReglaNegocioException("No se pueden agendar citas en fechas pasadas.");
        if (c.IdCita != 0)
        {
            var actual = Servicio.Ejecutar(() => CitaDatos.Obtener(c.IdCita))
                ?? throw new ReglaNegocioException("La cita no existe.");
            if (actual.Estado != "Programada")
                throw new ReglaNegocioException("Solo se pueden modificar citas programadas.");
        }
        Servicio.Ejecutar(() => CitaDatos.Guardar(c));
    }

    public static void Cancelar(int id)
    {
        if (Servicio.Ejecutar(() => CitaDatos.Cancelar(id)) == 0)
            throw new ReglaNegocioException("Solo se pueden cancelar citas programadas.");
    }

    public static void Atender(int idCita, int idTratamiento, string? diente, decimal? precio, decimal? monto, string? metodo)
    {
        if (precio is < 0) throw new ReglaNegocioException("El precio aplicado no puede ser negativo.");
        if (monto is > 0 && !Metodos.Contains(metodo))
            throw new ReglaNegocioException("Seleccione el método de pago del abono.");
        Servicio.Ejecutar(() => CitaDatos.Atender(idCita, idTratamiento, diente, precio, monto, metodo));
    }

    public static void RegistrarPago(int idCita, decimal monto, string metodo)
    {
        if (monto <= 0) throw new ReglaNegocioException("El monto debe ser mayor a cero.");
        if (!Metodos.Contains(metodo)) throw new ReglaNegocioException("Seleccione un método de pago válido.");
        Servicio.Ejecutar(() => CitaDatos.RegistrarPago(idCita, monto, metodo));
    }
}
