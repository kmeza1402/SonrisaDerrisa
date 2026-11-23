using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages.Pacientes;

public class IndexModel : PageModel
{
    [BindProperty(SupportsGet = true)] public string? Buscar { get; set; }
    public List<Paciente> Lista { get; set; } = [];

    public void OnGet()
    {
        try { Lista = Servicio.Ejecutar(() => PacienteDatos.Buscar(Buscar)); }
        catch (ReglaNegocioException ex) { TempData["Error"] = ex.Message; }
    }

    public IActionResult OnPostEliminar(int id)
    {
        try
        {
            Servicio.Ejecutar(() => PacienteDatos.Eliminar(id));
            TempData["Ok"] = "Paciente eliminado junto con su historial clínico.";
        }
        catch (ReglaNegocioException ex) { TempData["Error"] = ex.Message; }
        return RedirectToPage();
    }
}
