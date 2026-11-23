using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages.Pacientes;

public class EditarModel : PageModel
{
    [BindProperty] public Paciente Paciente { get; set; } = new();

    public IActionResult OnGet(int? id)
    {
        if (id is null) return Page();
        var p = Servicio.Ejecutar(() => PacienteDatos.Obtener(id.Value));
        if (p is null)
        {
            TempData["Error"] = "El paciente no existe.";
            return RedirectToPage("Index");
        }
        Paciente = p;
        return Page();
    }

    public IActionResult OnPost()
    {
        if (Paciente.FechaNacimiento > DateTime.Today)
            ModelState.AddModelError("Paciente.FechaNacimiento", "La fecha de nacimiento no puede ser futura.");
        if (!ModelState.IsValid) return Page();

        bool nuevo = Paciente.IdPaciente == 0;
        try
        {
            Servicio.Ejecutar(() => PacienteDatos.Guardar(Paciente));
            TempData["Ok"] = nuevo ? "Paciente e historial clínico registrados." : "Paciente actualizado.";
            return RedirectToPage("Index");
        }
        catch (ReglaNegocioException ex)
        {
            ModelState.AddModelError("", ex.Message);
            return Page();
        }
    }
}
