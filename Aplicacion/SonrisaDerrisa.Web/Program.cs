using System.Globalization;
using SonrisaDerrisa.Negocios;

CultureInfo.DefaultThreadCurrentCulture = CultureInfo.DefaultThreadCurrentUICulture = new CultureInfo("es-MX");

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();

// La cadena de conexión vive en User Secrets o en la configuración del entorno, nunca en el repositorio.
string cadena = builder.Configuration.GetConnectionString("SonrisaDerrisa")
    ?? throw new InvalidOperationException(
        "No se encontró ConnectionStrings:SonrisaDerrisa. " +
        "Configúrela con User Secrets para desarrollo o con una variable de entorno para producción.");
Servicio.Configurar(cadena);

var app = builder.Build();

// Todas las excepciones no controladas terminan en una pantalla entendible,
// sin exponer detalles internos de MySQL al usuario.
app.UseExceptionHandler("/Error");

app.UseRouting();
app.UseAuthorization();
app.MapStaticAssets();
app.MapRazorPages().WithStaticAssets();
app.Run();
