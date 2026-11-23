using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.AspNetCore.Mvc.Rendering;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages.Dentistas;

public class EditarModel : PageModel
{
    [BindProperty] public Dentista Dentista { get; set; } = new();
    public SelectList Especialidades { get; set; } = null!;

    public IActionResult OnGet(int? id)
    {
        Cargar();
        if (id is null) return Page();
        var d = Servicio.Ejecutar(() => DentistaDatos.Obtener(id.Value));
        if (d is null)
        {
            TempData["Error"] = "El dentista no existe.";
            return RedirectToPage("Index");
        }
        Dentista = d;
        return Page();
    }

    public IActionResult OnPost()
    {
        Cargar();
        if (!ModelState.IsValid) return Page();
        bool nuevo = Dentista.IdDentista == 0;
        try
        {
            Servicio.Ejecutar(() => DentistaDatos.Guardar(Dentista));
            TempData["Ok"] = nuevo ? "Dentista registrado." : "Dentista actualizado.";
            return RedirectToPage("Index");
        }
        catch (ReglaNegocioException ex)
        {
            ModelState.AddModelError("", ex.Message);
            return Page();
        }
    }

    private void Cargar() =>
        Especialidades = new SelectList(Servicio.Ejecutar(DentistaDatos.Especialidades), "Id", "Texto");
}
