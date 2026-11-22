using Microsoft.AspNetCore.Mvc.RazorPages;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages;

public class IndexModel : PageModel
{
    public List<(string Nombre, int Total)> Conteos { get; set; } = [];
    public string? Error { get; set; }

    public void OnGet()
    {
        try { Conteos = Servicio.Ejecutar(CitaDatos.Conteos); }
        catch (ReglaNegocioException ex) { Error = ex.Message; }
        catch (InvalidOperationException ex) { Error = ex.Message; }
    }
}
