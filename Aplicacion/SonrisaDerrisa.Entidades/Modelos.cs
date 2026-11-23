using System.ComponentModel.DataAnnotations;

namespace SonrisaDerrisa.Entidades;

public class Paciente
{
    public int IdPaciente { get; set; }

    [Required(ErrorMessage = "El nombre es obligatorio.")]
    [StringLength(50)]
    public string Nombre { get; set; } = "";

    [Required(ErrorMessage = "Los apellidos son obligatorios.")]
    [StringLength(80)]
    public string Apellidos { get; set; } = "";

    [DataType(DataType.Date)]
    [Display(Name = "Fecha de nacimiento")]
    public DateTime? FechaNacimiento { get; set; }

    [Required(ErrorMessage = "El teléfono es obligatorio.")]
    [RegularExpression(@"^[0-9]{10}$", ErrorMessage = "El teléfono debe tener 10 dígitos.")]
    [Display(Name = "Teléfono")]
    public string Telefono { get; set; } = "";

    [EmailAddress(ErrorMessage = "Correo no válido.")]
    [StringLength(100)]
    public string? Correo { get; set; }

    public DateTime FechaRegistro { get; set; }

    // Historial clínico (RN2: uno por paciente, se captura en el mismo formulario)
    public bool TieneHistorial { get; set; }
    [StringLength(200)] public string? Alergias { get; set; }
    [StringLength(200)] public string? Enfermedades { get; set; }
    [StringLength(200)] public string? Medicamentos { get; set; }

    public string NombreCompleto => $"{Nombre} {Apellidos}";
}

public class Dentista
{
    public int IdDentista { get; set; }

    [Required(ErrorMessage = "El nombre es obligatorio.")]
    [StringLength(50)]
    public string Nombre { get; set; } = "";

    [Required(ErrorMessage = "Los apellidos son obligatorios.")]
    [StringLength(80)]
    public string Apellidos { get; set; } = "";

    [Required(ErrorMessage = "La cédula es obligatoria.")]
    [StringLength(20)]
    [Display(Name = "Cédula profesional")]
    public string Cedula { get; set; } = "";

    [RegularExpression(@"^[0-9]{10}$", ErrorMessage = "El teléfono debe tener 10 dígitos.")]
    [Display(Name = "Teléfono")]
    public string? Telefono { get; set; }

    [Range(1, int.MaxValue, ErrorMessage = "Seleccione una especialidad.")]
    [Display(Name = "Especialidad")]
    public int IdEspecialidad { get; set; }

    public string? Especialidad { get; set; }
    public int Citas { get; set; }

    public string NombreCompleto => $"{Nombre} {Apellidos}";
}

public class Cita
{
    public int IdCita { get; set; }

    [Range(1, int.MaxValue, ErrorMessage = "Seleccione un paciente.")]
    [Display(Name = "Paciente")]
    public int IdPaciente { get; set; }

    [Range(1, int.MaxValue, ErrorMessage = "Seleccione un dentista.")]
    [Display(Name = "Dentista")]
    public int IdDentista { get; set; }

    [Required(ErrorMessage = "La fecha es obligatoria.")]
    [DataType(DataType.Date)]
    public DateTime? Fecha { get; set; }

    [Required(ErrorMessage = "La hora es obligatoria.")]
    [DataType(DataType.Time)]
    public TimeSpan? Hora { get; set; }

    [StringLength(150)]
    public string? Motivo { get; set; }

    public string Estado { get; set; } = "Programada";
}

/// <summary>Fila de la vista vw_agenda.</summary>
public class AgendaItem
{
    public int IdCita { get; set; }
    public DateTime Fecha { get; set; }
    public TimeSpan Hora { get; set; }
    public string Estado { get; set; } = "";
    public string? Motivo { get; set; }
    public int IdPaciente { get; set; }
    public string Paciente { get; set; } = "";
    public string Telefono { get; set; } = "";
    public int IdDentista { get; set; }
    public string Dentista { get; set; } = "";
    public string Especialidad { get; set; } = "";
    public string? Alergias { get; set; }
}

/// <summary>Fila de la vista vw_saldo_citas.</summary>
public class SaldoCita
{
    public int IdCita { get; set; }
    public DateTime Fecha { get; set; }
    public int IdPaciente { get; set; }
    public string Paciente { get; set; } = "";
    public string Dentista { get; set; } = "";
    public decimal Total { get; set; }
    public decimal Pagado { get; set; }
    public decimal Saldo { get; set; }
}

public class Opcion
{
    public int Id { get; set; }
    public string Texto { get; set; } = "";
    public decimal Precio { get; set; }
}
