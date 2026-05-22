---
tipo: "curso"
curso: "Aplicaciones Móviles"
curso_nombre: "Aplicaciones Móviles"
ciclo: "IX"
ruta_curso: "01_Universidad/IX/Aplicaciones Móviles"
semanas_total: 16
estado: "activo"
fecha_inicio: 2026-04-27
tags:
  - academia
  - curso
---

# Aplicaciones Móviles

| Propiedad | Valor |
|---|---|
| **Ciclo** | `= this.ciclo` |
| **Semanas** | `= this.semanas_total` |
| **Estado** | `= this.estado` |
| **Inicio** | 2026-04-27 |

---

## Descripcion del curso

> 

---

## Semanas

```dataview
TABLE WITHOUT ID
  link(file.link, semana) AS "Semana",
  fecha_inicio AS "Inicio",
  estado AS "Estado"
FROM ""
WHERE tipo = "semana" AND curso_nombre = "Aplicaciones Móviles" AND ciclo = "IX"
SORT file.name ASC
```

---

## Sesiones

```dataview
TABLE WITHOUT ID
  link(file.link, file.name) AS "Sesion",
  semana AS "Semana",
  sesion AS "Tipo",
  fecha AS "Fecha",
  estado AS "Estado"
FROM ""
WHERE tipo = "sesion" AND curso_nombre = "Aplicaciones Móviles" AND ciclo = "IX"
SORT fecha DESC
```

---

## Tareas

```dataview
TABLE WITHOUT ID
  link(file.link, titulo) AS "Tarea",
  semana AS "Semana",
  fecha_entrega AS "Entrega",
  estado AS "Estado"
FROM ""
WHERE tipo = "tarea" AND curso_nombre = "Aplicaciones Móviles" AND ciclo = "IX"
SORT fecha_asignacion DESC
```

---

## Notas generales

> 