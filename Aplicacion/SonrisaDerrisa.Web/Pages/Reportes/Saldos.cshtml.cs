using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using SonrisaDerrisa.Datos;
using SonrisaDerrisa.Entidades;
using SonrisaDerrisa.Negocios;

namespace SonrisaDerrisa.Web.Pages.Reportes;

/// <summary>Módulo de consulta/reporte sobre la vista vw_saldo_citas.</summary>
public class SaldosModel : PageModel
{
    [BindProperty(SupportsGet = true)] public string? Paciente { get; set; }
    [BindProperty(SupportsGet = true)] public bool SoloPendientes { get; set; } = true;
    public List<SaldoCita> Lista { get; set; } = [];

    public void OnGet()
    {
        if (Request.Query.Count > 0 && !Request.Query.ContainsKey(nameof(SoloPendientes)))
            SoloPendientes = false; // checkbox desmarcado
        try { Lista = Servicio.Ejecutar(() => CitaDatos.Saldos(Paciente, SoloPendientes)); }
        catch (ReglaNegocioException ex) { TempData["Error"] = ex.Message; }
    }
}
