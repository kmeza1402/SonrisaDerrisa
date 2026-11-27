using System.Diagnostics;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using MySql.Data.MySqlClient;

namespace SonrisaDerrisa.Web.Pages;

[ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
[IgnoreAntiforgeryToken]
public class ErrorModel : PageModel
{
    public string? RequestId { get; set; }
    public bool EsErrorBaseDatos { get; private set; }
    public string Titulo { get; private set; } = "No pudimos completar la solicitud";
    public string Mensaje { get; private set; } = "Ocurrió un problema inesperado. Intenta nuevamente.";

    public bool ShowRequestId => !string.IsNullOrEmpty(RequestId);

    public void OnGet()
    {
        RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier;

        Exception? error = HttpContext.Features.Get<IExceptionHandlerPathFeature>()?.Error;
        EsErrorBaseDatos = ContieneErrorBaseDatos(error);

        if (EsErrorBaseDatos)
        {
            Titulo = "No pudimos conectar con la clínica";
            Mensaje = "La base de datos no está disponible en este momento. " +
                      "Verifica la conexión e intenta nuevamente en unos segundos.";
        }
    }

    private static bool ContieneErrorBaseDatos(Exception? error)
    {
        while (error != null)
        {
            if (error is MySqlException || error is TimeoutException)
                return true;

            if (error is InvalidOperationException &&
                error.Message.Contains("ConnectionStrings", StringComparison.OrdinalIgnoreCase))
                return true;

            error = error.InnerException;
        }

        return false;
    }
}

