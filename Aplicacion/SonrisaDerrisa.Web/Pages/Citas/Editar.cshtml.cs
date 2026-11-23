using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.AspNetCore.Mvc.Rendering;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages.Citas;

public class EditarModel : PageModel
{
    [BindProperty] public Cita Cita { get; set; } = new();
    public SelectList Pacientes { get; set; } = null!;
    public SelectList Dentistas { get; set; } = null!;

    public IActionResult OnGet(int? id)
    {
        Cargar();
        if (id is null) return Page();
        var c = Servicio.Ejecutar(() => CitaDatos.Obtener(id.Value));
        if (c is null || c.Estado != "Programada")
        {
            TempData["Error"] = "Solo se pueden modificar citas programadas.";
            return RedirectToPage("Index");
        }
        Cita = c;
        return Page();
    }

    public IActionResult OnPost()
    {
        Cargar();
        if (!ModelState.IsValid) return Page();
        bool nueva = Cita.IdCita == 0;
        try
        {
            CitaNegocio.Guardar(Cita);
            TempData["Ok"] = nueva ? "Cita agendada." : "Cita reprogramada.";
            return RedirectToPage("Index");
        }
        catch (ReglaNegocioException ex)
        {
            ModelState.AddModelError("", ex.Message);
            return Page();
        }
    }

    private void Cargar()
    {
        Pacientes = new SelectList(Servicio.Ejecutar(PacienteDatos.Opciones), "Id", "Texto");
        Dentistas = new SelectList(Servicio.Ejecutar(DentistaDatos.Opciones), "Id", "Texto");
    }
}
