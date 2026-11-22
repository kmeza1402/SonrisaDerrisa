using System.Globalization;
using SonrisaDerrisa.Negocios;

CultureInfo.DefaultThreadCurrentCulture = CultureInfo.DefaultThreadCurrentUICulture = new CultureInfo("es-MX");

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();

// La cadena de conexión vive en User Secrets (ConnectionStrings:SonrisaDerrisa), nunca en el repositorio.
string? cadena = builder.Configuration.GetConnectionString("SonrisaDerrisa");
if (!string.IsNullOrWhiteSpace(cadena))
    Servicio.Configurar(cadena);

var app = builder.Build();

if (!app.Environment.IsDevelopment())
    app.UseExceptionHandler("/Error");

app.UseRouting();
app.UseAuthorization();
app.MapStaticAssets();
app.MapRazorPages().WithStaticAssets();
app.Run();
