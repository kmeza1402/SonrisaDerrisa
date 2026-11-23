using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages.Citas;

/// <summary>Operación multitabla transaccional: llama a sp_atender_cita
/// (actualiza cita, inserta detalle_cita y pago; todo o nada).</summary>
public class AtenderModel : PageModel
{
    [BindProperty(SupportsGet = true)] public int Id { get; set; }

    [BindProperty, Range(1, int.MaxValue, ErrorMessage = "Seleccione un tratamiento.")]
    public int IdTratamiento { get; set; }

    [BindProperty, RegularExpression(@"^[1-8][1-8]$", ErrorMessage = "Use notación FDI de dos dígitos (11 a 88).")]
    public string? Diente { get; set; }

    [BindProperty, Range(0, 999999, ErrorMessage = "El precio no puede ser negativo.")]
    public decimal? Precio { get; set; }

    [BindProperty, Range(0, 999999, ErrorMessage = "El abono no puede ser negativo.")]
    public decimal? Abono { get; set; }

    [BindProperty] public string? Metodo { get; set; }

    public AgendaItem? Cita { get; set; }
    public List<Opcion> Tratamientos { get; set; } = [];

    public IActionResult OnGet() => Cargar() ? Page() : RedirectToPage("Index");

    public IActionResult OnPost()
    {
        if (!Cargar()) return RedirectToPage("Index");
        if (!ModelState.IsValid) return Page();
        try
        {
            CitaNegocio.Atender(Id, IdTratamiento, Diente, Precio, Abono, Metodo);
            decimal saldo = Servicio.Ejecutar(() => CitaDatos.Saldo(Id));
            TempData["Ok"] = $"Cita #{Id} atendida. Saldo pendiente: {saldo:C}.";
            return RedirectToPage("Index");
        }
        catch (ReglaNegocioException ex)
        {
            ModelState.AddModelError("", ex.Message + " No se guardó ningún cambio.");
            return Page();
        }
    }

    private bool Cargar()
    {
        Cita = Servicio.Ejecutar(() => CitaDatos.Agenda(null, null, 0, null, null)).FirstOrDefault(c => c.IdCita == Id);
        if (Cita is null || Cita.Estado != "Programada")
        {
            TempData["Error"] = "Solo se pueden atender citas programadas.";
            return false;
        }
        Tratamientos = Servicio.Ejecutar(CitaDatos.Tratamientos);
        return true;
    }
}
