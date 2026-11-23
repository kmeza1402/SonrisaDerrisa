using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.AspNetCore.Mvc.Rendering;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages.Dentistas;

public class IndexModel : PageModel
{
    [BindProperty(SupportsGet = true)] public string? Buscar { get; set; }
    [BindProperty(SupportsGet = true)] public int Especialidad { get; set; }
    public List<Dentista> Lista { get; set; } = [];
    public SelectList Especialidades { get; set; } = null!;

    public void OnGet()
    {
        try
        {
            Especialidades = new SelectList(Servicio.Ejecutar(DentistaDatos.Especialidades), "Id", "Texto");
            Lista = Servicio.Ejecutar(() => DentistaDatos.Buscar(Buscar, Especialidad));
        }
        catch (ReglaNegocioException ex)
        {
            Especialidades = new SelectList(Array.Empty<Opcion>());
            TempData["Error"] = ex.Message;
        }
    }

    public IActionResult OnPostEliminar(int id)
    {
        try
        {
            Servicio.Ejecutar(() => DentistaDatos.Eliminar(id));
            TempData["Ok"] = "Dentista eliminado.";
        }
        catch (ReglaNegocioException ex) { TempData["Error"] = ex.Message; }
        return RedirectToPage();
    }
}
