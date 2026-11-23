using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.AspNetCore.Mvc.Rendering;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages.Citas;

public class IndexModel : PageModel
{
    [BindProperty(SupportsGet = true)] public DateTime? Desde { get; set; }
    [BindProperty(SupportsGet = true)] public DateTime? Hasta { get; set; }
    [BindProperty(SupportsGet = true)] public int Dentista { get; set; }
    [BindProperty(SupportsGet = true)] public string? Estado { get; set; }
    [BindProperty(SupportsGet = true)] public string? Paciente { get; set; }

    public List<AgendaItem> Lista { get; set; } = [];
    public SelectList Dentistas { get; set; } = new(Array.Empty<Opcion>());

    public void OnGet()
    {
        if (Desde > Hasta)
        {
            TempData["Error"] = "La fecha inicial no puede ser mayor que la final.";
            return;
        }
        try
        {
            Dentistas = new SelectList(Servicio.Ejecutar(DentistaDatos.Opciones), "Id", "Texto");
            Lista = Servicio.Ejecutar(() => CitaDatos.Agenda(Desde, Hasta, Dentista, Estado, Paciente));
        }
        catch (ReglaNegocioException ex) { TempData["Error"] = ex.Message; }
    }

    public IActionResult OnPostCancelar(int id)
    {
        try
        {
            CitaNegocio.Cancelar(id);
            TempData["Ok"] = $"La cita #{id} fue cancelada.";
        }
        catch (ReglaNegocioException ex) { TempData["Error"] = ex.Message; }
        return RedirectToPage();
    }
}
