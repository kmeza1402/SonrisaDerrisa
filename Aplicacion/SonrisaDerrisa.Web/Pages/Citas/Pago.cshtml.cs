using System.ComponentModel.DataAnnotations;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages.Citas;

public class PagoModel : PageModel
{
    [BindProperty(SupportsGet = true)] public int Id { get; set; }

    [BindProperty, Required(ErrorMessage = "Capture el monto."), Range(0.01, 999999, ErrorMessage = "El monto debe ser mayor a cero.")]
    public decimal? Monto { get; set; }

    [BindProperty, Required(ErrorMessage = "Seleccione el método de pago.")]
    public string? Metodo { get; set; }

    public SaldoCita? Cuenta { get; set; }

    public IActionResult OnGet() => Cargar() ? Page() : RedirectToPage("Index");

    public IActionResult OnPost()
    {
        if (!Cargar()) return RedirectToPage("Index");
        if (!ModelState.IsValid) return Page();
        try
        {
            CitaNegocio.RegistrarPago(Id, Monto!.Value, Metodo!);
            TempData["Ok"] = $"Pago de {Monto:C} registrado en la cita #{Id}.";
            return RedirectToPage("/Reportes/Saldos");
        }
        catch (ReglaNegocioException ex)
        {
            ModelState.AddModelError("", ex.Message);
            return Page();
        }
    }

    private bool Cargar()
    {
        Cuenta = Servicio.Ejecutar(() => CitaDatos.Saldos(null, false)).FirstOrDefault(s => s.IdCita == Id);
        if (Cuenta is null) TempData["Error"] = "Solo se registran pagos en citas atendidas.";
        return Cuenta is not null;
    }
}
