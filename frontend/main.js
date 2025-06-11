// Tecdoit front-end – main.js
// ------------------------------------------------
const BASE_URL = "http://127.0.0.1:8000";

// ── Helpers ───────────────────────────────────────────────────────────────
const getToken = () =>
  localStorage.getItem("tdToken") || sessionStorage.getItem("tdToken");
const saveToken = (token, remember) =>
  (remember ? localStorage : sessionStorage).setItem("tdToken", token);
const clearToken = () => {
  localStorage.removeItem("tdToken");
  sessionStorage.removeItem("tdToken");
};
const redirect = (url) => (window.location.href = url);

// ── Wrapper para JSON ────────────────────────────────────────────────────
async function api(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };
  if (options.body === undefined) {
    delete headers['Content-Type'];
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (!res.ok) throw await res.json();
  return res.status === 204 ? null : await res.json();
}

// ── Init según página ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  console.log('📄 DOMContentLoaded, page=', document.body.dataset.page);
  const page = document.body.dataset.page;
  switch(page) {
    case 'login': initLogin(); break;
    case 'home': initHome(); break;
    case 'editProfile': initEditProfile(); break;
    case 'listado': initListado(); break;
    case 'editor': initEditor(); break;
    case 'revision': initRevision(); break;
    case 'profile': initProfile(); break;
    default: console.warn('Página no reconocida:', page);
  }
});

// ───────── index.html (login) ────────────────────────────────────────────
function initLogin() {
  const emailEl = document.getElementById("email");
  const pwdEl = document.getElementById("password");
  const form = document.getElementById("loginForm");
  const rememberEl = document.getElementById("remember");
  const rememberIcon = document.getElementById("rememberIcon");
  const togglePwdBtn = document.getElementById("togglePassword");
  const togglePwdIcon = document.getElementById("togglePasswordIcon");
  const errEl = document.getElementById("loginError");

  rememberEl.addEventListener("change", () => {
    rememberIcon.src = rememberEl.checked
      ? "assets/icons/checkbox-selected.svg"
      : "assets/icons/checkbox-unselected.svg";
  });
  togglePwdBtn.addEventListener("click", () => {
    const type = pwdEl.type === "password" ? "text" : "password";
    pwdEl.type = type;
    togglePwdIcon.src =
      type === "password" ? "assets/icons/btn-show.svg" : "assets/icons/btn-hide.svg";
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errEl.classList.add("hidden");
    const params = new URLSearchParams();
    params.append("username", emailEl.value);
    params.append("password", pwdEl.value);
    try {
      const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: params,
      });
      if (!res.ok) {
        const errData = await res.json();
        const msg =
          errData.detail || (Array.isArray(errData) ? errData.map((x) => x.msg).join(", ") : "Error");
        throw new Error(msg);
      }
      const data = await res.json();
      saveToken(data.access_token, rememberEl.checked);
      redirect("inicio.html");
    } catch (er) {
      errEl.textContent = er.message;
      errEl.classList.remove("hidden");
    }
  });
}

// ───────── inicio.html (dashboard) ───────────────────────────────────────
async function initHome() {
  if (!getToken()) return redirect("index.html");

  const nameEl    = document.getElementById("userName");
  const metaEl    = document.getElementById("userMeta");
  const avatarEl  = document.getElementById("avatarHome");
  const emailEl   = document.getElementById("userEmail");
  const titleEl   = document.getElementById("userTitle");
  const cargoEl   = document.getElementById("userCargo");
  const bioEl     = document.getElementById("userBio");
  const editBtn   = document.getElementById("editProfileBtn");
  const logoutBtn = document.getElementById("logoutBtn");
  const logoHome = document.getElementById("logoHome");
  const createQuestionBtn = document.getElementById("createQuestionBtn");

  logoutBtn.addEventListener("click", () => {
    clearToken();
    redirect("index.html");
  });
  editBtn.addEventListener("click", () => {
    redirect("editarMiPerfil.html");
  });
  if(logoHome) {
    logoHome.addEventListener("click", () => {
      redirect("listadoPreguntas.html")
    })
  }
  
  createQuestionBtn.addEventListener("click", () => {
      sessionStorage.removeItem("tdSelected");
      redirect("crearPreguntas.html");
  });

  try {
    const me = await api("/profesores/me");
    nameEl.textContent = `${me.nombre} ${me.apellido}`;
    metaEl.textContent = `${me.rol === "admin" ? "Administrador" : "Autor"} · ${me.campus || "Sin campus"}`;
    if (me.avatar_url) avatarEl.src = me.avatar_url;
    emailEl.textContent = me.correo || "—";
    titleEl.textContent = me.titulo || "—";
    cargoEl.textContent = me.cargo || "—";
    bioEl.textContent   = me.bio    || "—";
  } catch {
    clearToken();
    redirect("index.html");
  }
}

// ───────── editarMiPerfil.html ──────────────────────────────────────────
async function initEditProfile() {
  if (!getToken()) return redirect("index.html");

  const form          = document.getElementById("profileForm");
  const avatarInput   = document.getElementById("avatar");
  const avatarPreview = document.getElementById("avatarPreview");
  const cancelBtn     = document.getElementById("cancelEditBtn");
  const errEl         = document.getElementById("profileError");

  cancelBtn.addEventListener("click", () => redirect("inicio.html"));

  try {
    const me = await api("/profesores/me");
    form.nombre.value   = me.nombre || "";
    form.apellido.value = me.apellido || "";
    form.correo.value   = me.correo || "";
    form.campus.value   = me.campus || "";
    form.titulo.value   = me.titulo || "";
    form.cargo.value    = me.cargo || "";
    form.bio.value      = me.bio || "";
    if (me.avatar_url) avatarPreview.src = me.avatar_url;
  } catch {
    errEl.textContent = "No se pudieron cargar los datos.";
    errEl.classList.remove("hidden");
  }

  avatarInput.addEventListener("change", () => {
    const file = avatarInput.files[0];
    if (file) {
      avatarPreview.src = URL.createObjectURL(file);
      avatarPreview.onload = () => URL.revokeObjectURL(avatarPreview.src);
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errEl.classList.add("hidden");

    try {
      await api("/profesores/me", {
        method: "PATCH",
        body: JSON.stringify({
          nombre:   form.nombre.value,
          apellido: form.apellido.value,
          correo:   form.correo.value,
          campus:   form.campus.value,
          titulo:   form.titulo.value,
          cargo:    form.cargo.value,
          bio:      form.bio.value,
        }),
      });

      if (avatarInput.files[0]) {
        const fd = new FormData();
        fd.append("avatar", avatarInput.files[0]);
        const res = await fetch(`${BASE_URL}/profesores/me/avatar`, {
          method: "POST",
          headers: { Authorization: `Bearer ${getToken()}` },
          body: fd,
        });
        if (!res.ok) throw await res.json();
      }

      redirect("inicio.html");
    } catch (error) {
      const msg =
        error.detail ||
        (Array.isArray(error) ? error.map((x) => x.msg).join(", ") : "Error al guardar");
      errEl.textContent = msg;
      errEl.classList.remove("hidden");
    }
  });
}

// ─── PAGE: listadoPreguntas.html ──────────────────────────────────────
async function initListado() {
    document.getElementById("logoListado").onclick = () => redirect("listadoPreguntas.html");
    document.getElementById("avatarListado").onclick = () => redirect("inicio.html");
  
    const me = await api("/profesores/me");
    const myId = me.id_profesor;

    const avatarListadoEl = document.getElementById("avatarListado");
    if(avatarListadoEl && me.avatar_url) {
        avatarListadoEl.src = me.avatar_url;
    }
    
    const pageSize = 12; let page = 1; let allQuestions = [];
    const state = { sortKey: "id_pregunta", sortDir: "asc", selected: new Set() };
    const tbody = document.getElementById("pregBody");
    const reviewBtn = document.getElementById("reviewBtn");
    const editBtn = document.getElementById("editDraftBtn");
    
    allQuestions = await api("/preguntas/");
    
    function normalize(str) {
      return (str || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
    }
  
    function filterList() {
      return allQuestions.filter(p => {
        const est = normalize(p.estado);
        if (p.id_profesor === myId && est === "borrador") return true;
        if (p.id_profesor !== myId && est.includes("revision")) return true;
        if (p.id_profesor === myId && est === "rechazada") return true;
        return false;
      });
    }
    
    function sortList(list) {
      return list.sort((a,b)=>{
        const valA = a[state.sortKey];
        const valB = b[state.sortKey];
        const dir = state.sortDir === "asc" ? 1 : -1;
        if (valA < valB) return -1 * dir;
        if (valA > valB) return 1 * dir;
        return 0;
      });
    }

    function paginated(list){
      const start = (page-1)*pageSize; return list.slice(start,start+pageSize);
    }

    function refreshButtons() {
      const selArr = Array.from(state.selected).map(id=>filtered.find(p=>p.id_pregunta==id));
      const allRevision = selArr.length > 0 && selArr.every(p=>p && p.estado==="en revisión");
      const allEdit = selArr.length > 0 && selArr.every(p=>p && ["borrador","rechazada"].includes(p.estado));
      reviewBtn.disabled = !allRevision;
      editBtn.disabled = !allEdit;
    }
  
    let filtered = [];
    function render() {
      filtered = sortList(filterList());
      const pageCount = Math.ceil(filtered.length/pageSize) || 1;
      page = Math.min(page,pageCount);
      const rows = paginated(filtered);
      tbody.innerHTML = rows.map(p=>`<tr>
        <td class="px-2"><input type="checkbox" data-id="${p.id_pregunta}" class="rowChk w-4 h-4" ${state.selected.has(p.id_pregunta)?"checked":""}></td>
        <td class="px-2">${p.id_pregunta}</td><td class="px-2 truncate max-w-xs" title="${p.enunciado}">${p.enunciado}</td>
        <td class="px-2">${p.tipo.toUpperCase()}</td><td class="px-2">${p.id_isla}</td>
        <td class="px-2">
            ${p.temas.map(t => `<span class="inline-block bg-indigo-100 text-indigo-800 text-xs px-2 py-0.5 rounded-full mr-1">${t.nombre}</span>`).join("")}
            ${p.temas.length > 2 ? `<button class="temaBtn" data-id="${p.id_pregunta}">...</button>` : ''}
        </td>
        <td class="px-2">${["","Fácil","Medio","Difícil"][p.dificultad]}</td>
        <td class="px-2">${p.estado}</td><td class="px-2">${new Date(p.fecha_creacion).toLocaleDateString()}</td>
        <td class="px-2 space-x-1">
          <img src="assets/icons/btn-revisar.svg" data-act="rev" data-id="${p.id_pregunta}" class="cursor-pointer inline-block ${p.estado==='en revisión' ? '' : 'opacity-20 pointer-events-none'}">
          <img src="assets/icons/btn-editar.svg"  data-act="edit" data-id="${p.id_pregunta}" class="cursor-pointer inline-block ${['borrador','rechazada'].includes(p.estado) ? '' : 'opacity-20 pointer-events-none'}">
        </td>
      </tr>`).join("");
      document.getElementById("pagerInfo").textContent = `Mostrando ${rows.length} de ${filtered.length} preguntas | Página ${page} de ${pageCount}`;
      refreshButtons();
    }

    render();
  
    document.querySelectorAll("th.sortable").forEach(th=>{
      th.onclick = ()=>{ const key = th.dataset.key; state.sortDir = state.sortKey===key && state.sortDir==="asc"?"desc":"asc"; state.sortKey = key; render(); };
    });
  
    document.getElementById("prevPage").onclick = ()=>{ if(page>1){page--;render();}};
    document.getElementById("nextPage").onclick = ()=>{ const max=Math.ceil(filtered.length/pageSize)||1; if(page<max){page++;render();}};
  
    tbody.addEventListener("change", (e)=>{
      if (!e.target.classList.contains('rowChk')) return;
      const id = Number(e.target.dataset.id);
      if (e.target.checked) state.selected.add(id);
      else state.selected.delete(id);
      refreshButtons();
    });
    document.getElementById("checkAll").onchange = (e)=>{
      const checked = e.target.checked; 
      paginated(filtered).forEach(p=>checked?state.selected.add(p.id_pregunta):state.selected.delete(p.id_pregunta)); 
      render(); 
    };
  
    const temaPopover = document.getElementById("temaPopover");
    document.body.addEventListener("click", (e)=>{
      if (e.target.classList.contains("temaBtn")) {
        e.stopPropagation();
        const p = filtered.find(x => x.id_pregunta == e.target.dataset.id);
        temaPopover.innerHTML = p.temas.map(t => `<p class="font-semibold">${t.nombre}</p><p class="text-xs text-gray-600 mb-2">${t.descripcion}</p>`).join("") || "Sin temas";
        const rect = e.target.getBoundingClientRect();
        temaPopover.style.top = `${rect.bottom + window.scrollY}px`;
        temaPopover.style.left = `${rect.left + window.scrollX}px`;
        temaPopover.classList.remove("hidden");
      } else if(!temaPopover.contains(e.target)) {
        temaPopover.classList.add("hidden");
      }
    });
  
    const handleAction = (ids, action) => {
        if (!ids || ids.length === 0) return;
        sessionStorage.setItem('tdSelected', JSON.stringify(ids));
        const destination = action === 'edit' ? 'crearPreguntas.html' : 'revisionPreguntas.html';
        redirect(destination);
    };

    tbody.addEventListener('click', e => {
      const act = e.target.dataset.act;
      if (!act) return;
      const id  = Number(e.target.dataset.id);
      const p   = filtered.find(x => x.id_pregunta === id);
      if (!p) return;
    
      if (act === 'edit' && ['borrador','rechazada'].includes(p.estado)) {
        handleAction([id], 'edit');
      }
      if (act === 'rev' && p.estado === 'en revisión') {
        handleAction([id], 'review');
      }
    });
    
    reviewBtn.onclick = () => handleAction([...state.selected], 'review');
    editBtn.onclick = () => handleAction([...state.selected], 'edit');
}
  
// ─── PAGE: crearPreguntas.html ────────────────────────────────────────
async function initEditor() {
    document.getElementById("logoEditor").onclick  = () => redirect("listadoPreguntas.html");
    document.getElementById("avatarEditor").onclick = () => redirect("inicio.html");
  
    const ids = JSON.parse(sessionStorage.getItem("tdSelected") || "[]");
    console.log("Editor iniciado con los IDs:", ids);
  
    let islas, temas, questions = [], me;
    try {
      me = await api("/profesores/me");
      islas = await api("/islas");
      temas = await api("/temas/");
      if (ids.length > 0) {
        const questionResults = await Promise.allSettled(ids.map(id => api(`/preguntas/${id}`)));
        questions = questionResults
          .filter(result => result.status === 'fulfilled')
          .map(result => result.value);
      }
    } catch (error) {
      console.error("Error fatal durante la carga de datos:", error);
      alert(`No se pudieron cargar los datos básicos para el editor. Causa: ${error.detail || 'Error desconocido'}. Volviendo al listado.`);
      return redirect("listadoPreguntas.html");
    }

    const listEl      = document.getElementById("questionList");
    const enunInput   = document.getElementById("enunciadoInput");
    const optionList  = document.getElementById("optionList");
    const addOptBtn   = document.getElementById("addOptionBtn");
    const islaSelect  = document.getElementById("islaSelect");
    const difSelect   = document.getElementById("difSelect");
    const randSwitch  = document.getElementById("randSwitch");
    const vfSwitch    = document.getElementById("vfSwitch");
    const cbSwitch    = document.getElementById("cbSwitch");
    const temaList    = document.getElementById("temaList");
    const sendBtn     = document.getElementById("sendBtn");
    const sendAllBtn  = document.getElementById("sendAllBtn");
    const addQuestionBtn = document.getElementById("addQuestionBtn");
    const avatarEditorEl = document.getElementById("avatarEditor");

    if(avatarEditorEl && me.avatar_url) {
        avatarEditorEl.src = me.avatar_url;
    }

    islaSelect.innerHTML = islas.map(i => `<option value="${i.id_isla}">${i.nombre || 'Isla ' + i.id_isla}</option>`).join("");
    temaList.innerHTML = temas.map(t =>
      `<label class="flex items-center space-x-2 p-1 hover:bg-gray-100 rounded-md cursor-pointer">
         <input type="checkbox" class="temaChk" value="${t.id_tema}">
         <span>${t.nombre}</span>
       </label>`
    ).join("");

    let currentIdx = 0;

    function render() {
      const hasQuestions = questions.length > 0;
      sendAllBtn.disabled = !hasQuestions;
      sendBtn.disabled = !hasQuestions;

      if (!hasQuestions) {
        listEl.innerHTML = '<li class="text-center text-gray-500 p-4">No hay preguntas. ¡Agrega una!</li>';
        enunInput.value = '';
        optionList.innerHTML = '';
        return;
      }
      
      const q = questions[currentIdx];

      listEl.innerHTML = questions.map((p, i) =>
        `<li data-idx="${i}" class="cursor-pointer px-2 py-1.5 rounded-md truncate ${i === currentIdx ? 'bg-indigo-100 text-indigo-800 font-semibold' : 'text-gray-600 hover:bg-gray-50'}">
           <span class="font-bold mr-2">${p.id_pregunta || 'Nueva'}</span>
           ${(p.enunciado || "Sin enunciado").slice(0, 20)}...
         </li>`
      ).join("");

      enunInput.value = q.enunciado || "";
      optionList.innerHTML = (q.opciones || []).map((opt, idx) =>
        `<li class="flex items-center space-x-2 my-1">
           <button data-idx="${idx}" class="optCorrect w-8 h-8 flex-shrink-0 flex items-center justify-center font-bold border rounded-md ${opt.es_correcta ? 'bg-green-200 border-green-400' : 'bg-gray-100 border-gray-300'}">${String.fromCharCode(65 + idx)}</button>
           <input type="text" data-idx="${idx}" class="optText flex-1 border border-gray-300 rounded-md px-3 py-1.5" value="${opt.texto}" placeholder="Texto de la opción"/>
           <button data-idx="${idx}" class="delOptBtn text-red-400 hover:text-red-600 font-bold text-lg px-2 flex-shrink-0">×</button>
         </li>`
      ).join("");

      islaSelect.value = q.id_isla;
      difSelect.value  = q.dificultad;
      randSwitch.checked = q.randomizar;
      vfSwitch.checked   = q.tipo === "vf";
      cbSwitch.checked   = q.tipo === "checkbox";

      const temaIDsDeLaPregunta = (q.temas || []).map(t => t.id_tema);
      document.querySelectorAll(".temaChk").forEach(chk => {
        chk.checked = temaIDsDeLaPregunta.includes(Number(chk.value));
      });
    }

    listEl.addEventListener("click", e => {
      const li = e.target.closest("li[data-idx]");
      if (li && Number(li.dataset.idx) !== currentIdx) {
        currentIdx = Number(li.dataset.idx);
        render();
      }
    });
    
    enunInput.addEventListener('input', () => { if(questions[currentIdx]) questions[currentIdx].enunciado = enunInput.value; });
    islaSelect.addEventListener('change', () => { if(questions[currentIdx]) questions[currentIdx].id_isla = Number(islaSelect.value); });
    difSelect.addEventListener('change', () => { if(questions[currentIdx]) questions[currentIdx].dificultad = Number(difSelect.value); });
    randSwitch.addEventListener('change', () => { if(questions[currentIdx]) questions[currentIdx].randomizar = randSwitch.checked; });
    
    temaList.addEventListener("change", () => {
      if (!questions[currentIdx]) return;
      const q = questions[currentIdx];
      const selectedTemaObjects = [...temaList.querySelectorAll(".temaChk:checked")]
        .map(chk => temas.find(t => t.id_tema === Number(chk.value)))
        .filter(Boolean);
      q.temas = selectedTemaObjects;
    });

    optionList.addEventListener('input', e => {
      if (e.target.classList.contains('optText') && questions[currentIdx]) {
        questions[currentIdx].opciones[e.target.dataset.idx].texto = e.target.value;
      }
    });

    optionList.addEventListener('click', e => {
      if (!questions[currentIdx]) return;
      const btn = e.target.closest('button');
      if (!btn) return;
      const idx = Number(btn.dataset.idx);
      const q = questions[currentIdx];

      if (btn.classList.contains('delOptBtn')) {
        q.opciones.splice(idx, 1);
        render();
      }
      if (btn.classList.contains('optCorrect')) {
        if (q.tipo === 'checkbox') {
          q.opciones[idx].es_correcta = !q.opciones[idx].es_correcta;
        } else {
          q.opciones.forEach((opt, i) => opt.es_correcta = (i === idx));
        }
        render();
      }
    });

    addOptBtn.addEventListener('click', () => {
      if (questions[currentIdx] && questions[currentIdx].tipo !== 'vf') {
        questions[currentIdx].opciones.push({ texto: '', es_correcta: false });
        render();
      }
    });

    vfSwitch.addEventListener('change', () => {
        if (!questions[currentIdx]) return;
        const q = questions[currentIdx];
        if (vfSwitch.checked) {
            cbSwitch.checked = false; 
            q.tipo = "vf";
            q.opciones = [
                { texto: "Verdadero", es_correcta: false },
                { texto: "Falso", es_correcta: false }
            ];
        } else {
            q.tipo = "abc";
        }
        render();
    });
    cbSwitch.addEventListener('change', () => {
        if (!questions[currentIdx]) return;
        const q = questions[currentIdx];
        if (cbSwitch.checked) {
            vfSwitch.checked = false;
            q.tipo = "checkbox";
        } else {
            q.tipo = "abc";
            const firstCorrect = q.opciones.find(o => o.es_correcta);
            q.opciones.forEach(o => o.es_correcta = (o === firstCorrect));
        }
        render();
    });

    addQuestionBtn.addEventListener('click', () => {
      const newQ = {
        isNew: true,
        enunciado: "",
        tipo: "abc",
        id_isla: islas.length > 0 ? islas[0].id_isla : 1,
        dificultad: 1,
        randomizar: false,
        temas: [],
        opciones: [
          { texto: "", es_correcta: false },
          { texto: "", es_correcta: false }
        ]
      };
      questions.push(newQ);
      currentIdx = questions.length - 1;
      render();
    });

    function validateQuestion(q) {
      if (!q.enunciado.trim()) {
        alert("El enunciado no puede estar vacío.");
        return false;
      }
      if (q.opciones.length < 2) {
        alert("La pregunta debe tener al menos dos opciones.");
        return false;
      }
      if (q.opciones.some(opt => !opt.texto.trim())) {
        alert("El texto de todas las opciones es obligatorio.");
        return false;
      }
      const correctCount = q.opciones.filter(opt => opt.es_correcta).length;
      if (q.tipo === 'abc' || q.tipo === 'vf') {
        if (correctCount !== 1) {
          alert("Las preguntas de tipo 'Selección Única' o 'V/F' deben tener EXACTAMENTE UNA respuesta correcta.");
          return false;
        }
      }
      if (q.tipo === 'checkbox') {
        if (correctCount < 1) {
          alert("Las preguntas de 'Selección Múltiple' deben tener AL MENOS UNA respuesta correcta.");
          return false;
        }
      }
      return true;
    }

    async function saveOrUpdateDraft(q) {
      const payload = {
          enunciado: q.enunciado,
          tipo: q.tipo,
          id_isla: q.id_isla,
          dificultad: q.dificultad,
          randomizar: q.randomizar,
          temas: (q.temas || []).map(t => t.id_tema),
          opciones: (q.opciones || []).map(opt => ({
              texto: opt.texto,
              es_correcta: opt.es_correcta,
              ...(opt.id_opcion && !opt.isNew ? { id_opcion: opt.id_opcion } : {})
          }))
      };

      if (q.isNew) {
        console.log("Creando nuevo borrador (POST /preguntas/)...", payload);
        const newQuestionData = await api("/preguntas/", { method: "POST", body: JSON.stringify(payload) });
        Object.assign(q, newQuestionData, { isNew: false });
        console.log("Borrador creado con ID:", q.id_pregunta);
      } else {
        console.log(`Actualizando borrador ${q.id_pregunta} (PATCH /preguntas/${q.id_pregunta})...`, payload);
        await api(`/preguntas/${q.id_pregunta}`, { method: "PATCH", body: JSON.stringify(payload) });
      }
    }

    async function submitForReview(q) {
      if (!validateQuestion(q)) return false;

      try {
        await saveOrUpdateDraft(q);
        console.log(`Enviando a revisión (POST /preguntas/${q.id_pregunta}/submit)...`);
        await api(`/preguntas/${q.id_pregunta}/submit`, { method: "POST" });
        alert(`Pregunta ${q.id_pregunta} enviada a revisión.`);
        return true;
      } catch (err) {
        console.error("Error en el proceso de envío:", err);
        const errorMsg = err.detail && Array.isArray(err.detail) 
            ? err.detail.map(d => `${d.loc ? d.loc.join('->') : ''}: ${d.msg}`).join('\n') 
            : (err.detail || "Error desconocido");
        alert(`Error al enviar pregunta: ${errorMsg}`);
        return false;
      }
    }

    sendBtn.onclick = async () => {
      if (!questions[currentIdx]) return;
      const success = await submitForReview(questions[currentIdx]);
      if (success) {
        questions.splice(currentIdx, 1);
        if (questions.length === 0) {
          sessionStorage.removeItem('tdSelected');
          return redirect('listadoPreguntas.html');
        }
        currentIdx = Math.max(0, currentIdx - 1);
        render();
      }
    };

    sendAllBtn.onclick = async () => {
      for (const q of [...questions]) {
        const success = await submitForReview(q);
        if (!success) {
            alert(`El envío masivo se detuvo debido a un error con la pregunta "${(q.enunciado || 'Nueva').slice(0,20)}...".`);
            return;
        }
      }
      alert("Todas las preguntas han sido enviadas a revisión exitosamente.");
      sessionStorage.removeItem('tdSelected');
      redirect('listadoPreguntas.html');
    };

    if (ids.length === 0) {
      addQuestionBtn.click();
    } else {
      render();
    }
}


// ─── PAGE: revisionPreguntas.html ──────────────────────────────────────
async function initRevision(){
    document.getElementById("logoRevision").onclick = () => redirect("listadoPreguntas.html");
    document.getElementById("avatarRevision").onclick = () => redirect("inicio.html");
    
    let ids = JSON.parse(sessionStorage.getItem("tdSelected") || "[]");
    if (!ids.length) return redirect("listadoPreguntas.html");

    const revList = document.getElementById("revList");
    const enunImg = document.getElementById("revEnunImg");
    const enunText = document.getElementById("revEnunText");
    const optsDiv = document.getElementById("revOpts");
    const comment = document.getElementById("revComment");
    const acceptBtn = document.getElementById("acceptBtn");
    const rejectBtn = document.getElementById("rejectBtn");
    const autorAvatar = document.getElementById("revAutorAvatar");
    const autorNombre = document.getElementById("revAutorNombre");
    const autorCargo = document.getElementById("revAutorCargo");
    const viewProfileBtn = document.getElementById("viewProfileBtn");
    const avatarRevisionEl = document.getElementById("avatarRevision");

    let currentIdx = 0;
    let preguntas = [];
    
    try {
        const me = await api("/profesores/me");
        if(avatarRevisionEl && me.avatar_url) {
            avatarRevisionEl.src = me.avatar_url;
        }

        preguntas = await Promise.all(ids.map(id => api(`/preguntas/${id}`).catch(e => {
            console.error(`No se pudo cargar la pregunta ${id}`, e);
            return null;
        }))).then(results => results.filter(Boolean));
    } catch (e) {
        console.error("Error al cargar datos de revisión", e);
        alert("No se pudieron cargar los datos para la revisión.");
        return redirect("listadoPreguntas.html");
    }

    if (!preguntas.length) {
        alert("No se pudieron cargar las preguntas para revisión.");
        return redirect("listadoPreguntas.html");
    }

    function renderList() {
        revList.innerHTML = preguntas.map((p, i) => 
            `<li data-idx="${i}" class="px-2 py-1 rounded cursor-pointer ${i === currentIdx ? "bg-indigo-200" : "hover:bg-gray-100"}">
                <span class="font-semibold text-indigo-600 mr-1">${p.id_pregunta}</span>
                ${p.enunciado.slice(0, 30)}...
            </li>`
        ).join("");
    }

    async function renderCurrent() {
        const p = preguntas[currentIdx];
        if (!p) {
            if (preguntas.length > 0) { 
                currentIdx = 0;
                return renderCurrent();
            } else {
                alert("Todas las preguntas han sido revisadas.");
                return redirect("listadoPreguntas.html");
            }
        }

        if (p.url_imagen && p.url_imagen.startsWith('http')) {
            enunImg.src = p.url_imagen;
            enunImg.onerror = () => {
                enunText.textContent = p.enunciado;
                enunImg.classList.add("hidden");
                enunText.classList.remove("hidden");
            };
            enunImg.onload = () => {
                enunText.classList.add("hidden");
                enunImg.classList.remove("hidden");
            };
        } else {
            enunText.textContent = p.enunciado;
            enunImg.classList.add("hidden");
            enunText.classList.remove("hidden");
        }

        optsDiv.innerHTML = p.opciones.map(o => 
            `<div class="px-4 py-2 border rounded text-center ${o.es_correcta ? "border-green-400 bg-green-50" : "border-red-400 bg-red-50"}">
                ${o.url_imagen ? `<img src="${o.url_imagen}" class="max-w-full"/>` : o.texto}
            </div>`
        ).join("");

        try {
            const pr = await api(`/profesores/${p.id_profesor}`);
            if (pr.avatar_url) autorAvatar.src = pr.avatar_url;
            autorNombre.textContent = `${pr.nombre} ${pr.apellido}`;
            
            // *** CORRECCIÓN: Mostrar 'cargo' y 'título' correctamente ***
            const cargoYTitulo = [];
            if (pr.cargo && pr.cargo.trim()) {
                cargoYTitulo.push(pr.cargo.trim());
            }
            if (pr.titulo && pr.titulo.trim()) {
                cargoYTitulo.push(pr.titulo.trim());
            }
            autorCargo.textContent = cargoYTitulo.join(' · ');

            viewProfileBtn.onclick = () => redirect(`verPerfil.html?id=${p.id_profesor}`);
        } catch (e) {
            console.error("No se pudo cargar el perfil del autor", e);
            autorNombre.textContent = "Autor no encontrado";
            autorCargo.textContent = "";
        }
    }

    revList.onclick = (e) => {
        const li = e.target.closest("li[data-idx]");
        if (li) {
            currentIdx = Number(li.dataset.idx);
            renderList();
            renderCurrent();
        }
    };

    async function decide(decision) {
        const currentQ = preguntas[currentIdx];
        if (!currentQ) return;

        if (decision === "rechazada" && !comment.value.trim()) {
            alert("Debes escribir un comentario para rechazar la pregunta.");
            return;
        }

        try {
            await api(`/preguntas/${currentQ.id_pregunta}/decision`, {
                method: "POST",
                body: JSON.stringify({
                    decision: decision,
                    comentario: comment.value || ""
                })
            });

            preguntas.splice(currentIdx, 1);
            ids.splice(currentIdx, 1);
            sessionStorage.setItem("tdSelected", JSON.stringify(ids));

            if (!preguntas.length) {
                alert("Todas las preguntas han sido revisadas.");
                return redirect("listadoPreguntas.html");
            }
            
            currentIdx = Math.max(0, currentIdx - 1);
            renderList();
            renderCurrent();
            comment.value = "";
        } catch (err) {
            console.error("Error al tomar decisión:", err);
            alert("Hubo un error al procesar la decisión.");
        }
    }

    acceptBtn.onclick = () => decide("publicada");
    rejectBtn.onclick = () => decide("rechazada");

    renderList();
    renderCurrent();
}
  
// ─── PAGE: verPerfil.html ────────────────────────────────────────────
async function initProfile(){
    if(document.getElementById("logoProfile")) {
        document.getElementById("logoProfile").onclick=()=>redirect("listadoPreguntas.html");
    }
    const params=new URLSearchParams(location.search); const id=params.get("id"); if(!id) return redirect("listadoPreguntas.html");
    const pr=await api(`/profesores/${id}`);
    if(pr.avatar_url) document.getElementById("profAvatar").src=pr.avatar_url;
    document.getElementById("profNombre").textContent=`${pr.nombre} ${pr.apellido}`;
    document.getElementById("profMeta").textContent=`${pr.campus||""} – ${pr.rol==="admin"?"Administrador":"Autor"}`;
    document.getElementById("profCorreo").textContent=pr.correo; document.getElementById("profCorreo").href=`mailto:${pr.correo}`;
    document.getElementById("profTitulo").textContent=pr.titulo||"";
    document.getElementById("profCargo").textContent=pr.cargo||"";
    document.getElementById("profBio").textContent=pr.bio||"";
}
