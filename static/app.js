const API = "/api/materiales";
const $ = (id) => document.getElementById(id);
const CAMPOS = ["nombre", "tipo", "ubicacion", "fecha_adquisicion",
                "vida_util_anios", "estado", "uso"];
let registros = [];

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function llenarSelect(id, valores) {
  $(id).innerHTML = valores.map((v) => `<option value="${esc(v)}">${esc(v)}</option>`).join("");
}

function calcularVida(r) {
  const inicio = new Date(r.fecha_adquisicion + "T00:00:00Z");
  const fin = new Date(inicio);
  fin.setUTCFullYear(fin.getUTCFullYear() + r.vida_util_anios);
  const pct = Math.round(((Date.now() - inicio) / (fin - inicio)) * 100);
  return { fin: fin.toISOString().slice(0, 10), pct: Math.max(0, pct) };
}

function mostrarErrores(lista) {
  const ul = $("errores");
  ul.innerHTML = lista.map((m) => `<li>${esc(m)}</li>`).join("");
  ul.hidden = lista.length === 0;
}

function render() {
  $("vacio").hidden = registros.length > 0;
  $("tbody").innerHTML = registros.map((r) => {
    const v = calcularVida(r);
    const clase = v.pct >= 100 ? "rojo" : v.pct >= 75 ? "naranja" : "verde";
    return `<tr>
      <td>${esc(r.nombre)}</td>
      <td>${esc(r.tipo)}</td>
      <td>${esc(r.ubicacion)}</td>
      <td>${esc(r.fecha_adquisicion)}</td>
      <td>${r.vida_util_anios} años</td>
      <td>${v.fin}</td>
      <td><span class="badge ${clase}">${v.pct}%</span></td>
      <td>${esc(r.estado)}</td>
      <td>${esc(r.uso)}</td>
      <td class="fila-acciones">
        <button class="secundario" data-editar="${r.id}">Editar</button>
        <button class="peligro" data-borrar="${r.id}">Eliminar</button>
      </td>
    </tr>`;
  }).join("");
}

async function cargar() {
  const res = await fetch(API);
  registros = await res.json();
  render();
}

function resetForm() {
  $("form").reset();
  $("id").value = "";
  $("form-titulo").textContent = "Nuevo registro";
  $("btn-cancelar").hidden = true;
  mostrarErrores([]);
}

function editar(id) {
  const r = registros.find((x) => x.id === id);
  if (!r) return;
  $("id").value = r.id;
  CAMPOS.forEach((c) => { $(c).value = r[c]; });
  $("form-titulo").textContent = "Editar registro #" + r.id;
  $("btn-cancelar").hidden = false;
  mostrarErrores([]);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function borrar(id) {
  if (!confirm("¿Eliminar este registro?")) return;
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  if (res.ok || res.status === 404) {
    if ($("id").value === String(id)) resetForm();
    await cargar();
  } else {
    alert("No se pudo eliminar el registro.");
  }
}

$("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const datos = {};
  CAMPOS.forEach((c) => { datos[c] = $(c).value; });
  datos.vida_util_anios = $("vida_util_anios").value === "" ? null : Number($("vida_util_anios").value);

  const id = $("id").value;
  const res = await fetch(id ? `${API}/${id}` : API, {
    method: id ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });

  if (res.ok) {
    resetForm();
    await cargar();
  } else {
    const cuerpo = await res.json().catch(() => ({}));
    mostrarErrores(cuerpo.errores
      ? Object.entries(cuerpo.errores).map(([k, m]) => `${k}: ${m}`)
      : [cuerpo.error || "Error al guardar."]);
  }
});

$("btn-cancelar").addEventListener("click", resetForm);

$("tbody").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  if (b.dataset.editar) editar(Number(b.dataset.editar));
  if (b.dataset.borrar) borrar(Number(b.dataset.borrar));
});

async function iniciar() {
  const op = await (await fetch("/api/opciones")).json();
  llenarSelect("tipo", op.tipos);
  llenarSelect("estado", op.estados);
  llenarSelect("uso", op.usos);
  $("fecha_adquisicion").max = new Date().toISOString().slice(0, 10);
  await cargar();
}

iniciar();