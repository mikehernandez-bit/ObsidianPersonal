---
tipo: "curso"
curso: "Algoritmos Evolutivos y de Aprendizaje"
curso_nombre: "Algoritmos Evolutivos y de Aprendizaje"
ciclo: "IX"
ruta_curso: "01_Universidad/IX/Algoritmos Evolutivos y de Aprendizaje"
semanas_total: 16
estado: "activo"
fecha_inicio: 2026-05-16
tags:
  - academia
  - curso
---

# Algoritmos Evolutivos y de Aprendizaje

| Propiedad | Valor |
|---|---|
| **Ciclo** | `= this.ciclo` |
| **Semanas** | `= this.semanas_total` |
| **Estado** | `= this.estado` |
| **Inicio** | 2026-05-16 |

---

## Descripción del curso

> 

---

## Semanas

```dataview
TABLE WITHOUT ID
  link(file.link, semana) AS "Semana",
  fecha_inicio AS "Inicio",
  estado AS "Estado"
FROM ""
WHERE tipo = "semana" AND curso_nombre = "Algoritmos Evolutivos y de Aprendizaje" AND ciclo = "IX"
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
WHERE tipo = "sesion" AND curso_nombre = "Algoritmos Evolutivos y de Aprendizaje" AND ciclo = "IX"
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
WHERE tipo = "tarea" AND curso_nombre = "Algoritmos Evolutivos y de Aprendizaje" AND ciclo = "IX"
SORT fecha_asignacion DESC
```

---

## Notas generales

> 