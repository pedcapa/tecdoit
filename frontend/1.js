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
  const regBtn    = document.getElementById("registerProfesorBtn");
  const editBtn   = document.getElementById("editProfileBtn");
  const logoutBtn = document.getElementById("logoutBtn");

  logoutBtn.addEventListener("click", () => {
    clearToken();
    redirect("index.html");
  });
  editBtn.addEventListener("click", () => {
    redirect("editarMiPerfil.html");
  });
  logoHome.addEventListener("click", () => {
    redirect("listadoPreguntas.html")
  })

  try {
    const me = await api("/profesores/me");
    nameEl.textContent = `${me.nombre} ${me.apellido}`;
    metaEl.textContent = `${me.rol === "admin" ? "Administrador" : "Autor"} · ${me.campus || "Sin campus"}`;
    if (me.rol === "admin") regBtn.classList.remove("hidden");
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

  // Prefill
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

  // Preview al cambiar avatar
  avatarInput.addEventListener("change", () => {
    const file = avatarInput.files[0];
    if (file) {
      avatarPreview.src = URL.createObjectURL(file);
      avatarPreview.onload = () => URL.revokeObjectURL(avatarPreview.src);
    }
  });

  // Guardar perfil + avatar
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errEl.classList.add("hidden");

    try {
      // 1) PATCH JSON con campos de texto
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

      // 2) POST AVATAR si hay archivo
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
  console.log("initListado arrancó")
    // setup header nav
    document.getElementById("logoListado").onclick = () => redirect("listadoPreguntas.html");
    document.getElementById("avatarListado").onclick = () => redirect("inicio.html");
  
    const me = await api("/profesores/me"); const myId = me.id_profesor;
    const pageSize = 12; let page = 1; let allQuestions = [];
    const state = { sortKey: "id_pregunta", sortDir: "asc", selected: new Set() };
    const tbody = document.getElementById("pregBody");
    const reviewBtn = document.getElementById("reviewBtn");
    const editBtn = document.getElementById("editDraftBtn");
    
    const checkAll  = document.getElementById("checkAll");
    const logoListado = document.getElementById("logoListado");


    
    // fetch all questions once (simplest)
    allQuestions = await api("/preguntas/");
    console.log("allQuestions raw:", allQuestions);
    
    function normalize(str) {
      return (str || "")
        .toLowerCase()
        .normalize("NFD")                 // separa diacríticos
        .replace(/[\u0300-\u036f]/g, "")  // quita tildes
        .trim();
    }

  
    // ── helpers ─────────────────────────
    function filterList() {
      return allQuestions.filter(p => {
        const est = normalize(p.estado);
        if (p.id_profesor === myId && est === "borrador") return true;
        if (p.id_profesor !== myId && est.includes("revision")) return true;
        if (p.id_profesor === myId && est === "rechazada") return true;
        return false;
      });
    }
    
    // console.log("filteredList:", filterList());
    // filterAndRender();
    
    function sortList(list) {
      return list.sort((a,b)=>{
        const dir = state.sortDir === "asc" ? 1 : -1;
        return a[state.sortKey] > b[state.sortKey] ? dir : -dir;
      });
    }
    function paginated(list){
      const start = (page-1)*pageSize; return list.slice(start,start+pageSize);
    }
    function refreshButtons() {
      const selArr = Array.from(state.selected).map(id=>filtered.find(p=>p.id_pregunta==id));
      const allRevision = selArr.length && selArr.every(p=>p.estado==="en revisión");
      const allEdit     = selArr.length && selArr.every(p=>["borrador","rechazada"].includes(p.estado));
      reviewBtn.disabled = !allRevision; editBtn.disabled = !allEdit;
    }
  
    let filtered = [];
    function filterAndRender() {
      filtered = sortList(filterList());
      const pageCount = Math.ceil(filtered.length/pageSize) || 1;
      page = Math.min(page,pageCount);
      const rows = paginated(filtered);
      tbody.innerHTML = rows.map(p=>`<tr>
        <td class="px-2"><input type="checkbox" data-id="${p.id_pregunta}" class="rowChk w-4 h-4" ${state.selected.has(p.id_pregunta)?"checked":""}></td>
        <td class="px-2">${p.id_pregunta}</td><td class="px-2 truncate max-w-xs" title="${p.enunciado}">${p.enunciado}</td>
        <td class="px-2">${p.tipo.toUpperCase()}</td><td class="px-2">${p.id_isla}</td>
        <td class="px-2">
  ${
    p.temas
     .map(t => 
       `<span class="inline-block bg-indigo-100 text-indigo-800 text-xs px-2 py-0.5 rounded-full mr-1">${t.nombre}</span>`
     )
     .join("")
  }
  <button class="temaBtn" data-id="${p.id_pregunta}">•••</button>
</td>
        <td class="px-2">${["","Fácil","Medio","Difícil"][p.dificultad]}</td>
        <td class="px-2">${p.estado}</td><td class="px-2">${new Date(p.fecha_creacion).toLocaleDateString()}</td>
        <td class="px-2 space-x-1">
          <img src="assets/icons/btn-revisar.svg" data-act="rev" data-id="${p.id_pregunta}"
          class="${p.estado==='en revisión' ? '' : 'opacity-20 pointer-events-none'}">
          <img src="assets/icons/btn-editar.svg"  data-act="edit" data-id="${p.id_pregunta}"
          class="${['borrador','rechazada'].includes(p.estado) ? '' : 'opacity-20 pointer-events-none'}">
        </td>
      </tr>`).join("");
      document.getElementById("pagerInfo").textContent = `Mostrando ${rows.length} de ${filtered.length} preguntas | Página ${page} de ${pageCount}`;
      refreshButtons();
    }

    const tmp = filterList();
    console.log(">> filteredList (post-normalize):", tmp);
    filterAndRender();
  
    // ── sorting ──
    document.querySelectorAll("th.sortable").forEach(th=>{
      th.onclick = ()=>{ const key = th.dataset.key; state.sortDir = state.sortKey===key && state.sortDir==="asc"?"desc":"asc"; state.sortKey = key; filterAndRender(); };
    });
  
    // ── pagination ──
    document.getElementById("prevPage").onclick = ()=>{ if(page>1){page--;filterAndRender();}};
    document.getElementById("nextPage").onclick = ()=>{ const max=Math.ceil(filtered.length/pageSize)||1; if(page<max){page++;filterAndRender();}};
  
    // ── checkbox selection ──
    tbody.addEventListener("change", (e)=>{
      if (!e.target.classList.contains('rowChk')) return;
      const id = Number(e.target.dataset.id);
      console.log(`🛠️ checkbox fila ${id} → ${e.target.checked}`);

      if (e.target.checked) state.selected.add(id);
      else state.selected.delete(id);
      console.log("🛠️ state.selected ahora es:", [...state.selected]);

      // después recalculemos el disable de los botones:
      reviewBtn.disabled = ![...state.selected].every(id => {
        const p = filtered.find(x => x.id_pregunta === id);
        return p && p.estado === 'en revisión';
      });
      editBtn.disabled = ![...state.selected].every(id => {
        const p = filtered.find(x => x.id_pregunta === id);
        return p && ['borrador','rechazada'].includes(p.estado);
      });
    
    });
    document.getElementById("checkAll").onchange = (e)=>{
      const checked = e.target.checked; paginated(filtered).forEach(p=>checked?state.selected.add(p.id_pregunta):state.selected.delete(p.id_pregunta)); filterAndRender(); };
  
    // ── tema popover ──
    const temaPopover = document.getElementById("temaPopover"); const temasCache = await api("/temas/");
    document.body.addEventListener("click", (e)=>{
      if (e.target.classList.contains("temaBtn")) {
        const p = filtered.find(x => x.id_pregunta == e.target.dataset.id);
        temaPopover.innerHTML = p.temas
          .map(t => `<p class="font-semibold">${t.nombre}</p><p class="mb-2">${t.descripcion}</p>`)
          .join("") || "Sin temas";
        temaPopover.style.top = e.pageY+"px"; temaPopover.style.left = e.pageX+"px";
        temaPopover.classList.remove("hidden");
      } else if(!temaPopover.contains(e.target)) temaPopover.classList.add("hidden");
    });
  
    // ── inline action icons ──
    tbody.addEventListener('click', e => {
      const act = e.target.dataset.act;
      const id  = Number(e.target.dataset.id);
      const p   = filtered.find(x => x.id_pregunta === id);
      if (!p) return;
    
      if (act === 'edit' && ['borrador','rechazada'].includes(p.estado)) {
        console.log("🛠️ icono edit individual clicado id=", id);
        // solo ese ID
        sessionStorage.setItem('tdSelected', JSON.stringify([id]));
        redirect('crearPreguntas.html');
      }
      if (act === 'rev' && p.estado === 'en revisión') {
        console.log("🛠️ botón editar borrador múltiple →", [...state.selected]);

        sessionStorage.setItem('tdSelected', JSON.stringify([id]));
        redirect('revisionPreguntas.html');
      }
    });
    
    reviewBtn.onclick = () => {
      sessionStorage.setItem('tdSelected', JSON.stringify([...state.selected]));
      redirect('revisionPreguntas.html');
    };
    editBtn.onclick = () => {
      sessionStorage.setItem('tdSelected', JSON.stringify([...state.selected]));
      redirect('crearPreguntas.html');
    };
    
    function goReview(){ sessionStorage.setItem("tdSelected", JSON.stringify([...state.selected])); redirect("revisionPreguntas.html"); }
    function goEdit(){ sessionStorage.setItem("tdSelected", JSON.stringify([...state.selected])); redirect("crearPreguntas.html"); }
  }
  
  // ─── PAGE: crearPreguntas.html ────────────────────────────────────────
  async function initEditor() {
    // navegación
    document.getElementById("logoEditor").onclick  = () => redirect("listadoPreguntas.html");
    document.getElementById("avatarEditor").onclick = () => redirect("inicio.html");
  
    // 1) Carga IDs seleccionados
    const ids = JSON.parse(sessionStorage.getItem("tdSelected") || "[]");
    if (!ids.length) return redirect("listadoPreguntas.html");
    console.log("🛠 initEditor, ids:", ids);
  
    // 2) Trae las preguntas y filtra nulas
    let questions = await Promise.all(
      ids.map(id => api(`/preguntas/${id}`).catch(err => {
        console.error("falló cargando", id, err);
        return null;
      }))
    );
    questions = questions.filter(q => q && q.id_pregunta);
    console.log("🛠 preguntas válidas:", questions);
  
    if (!questions.length) return redirect("listadoPreguntas.html");
  
    // 3) DOM refs
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
  
    // --- FIX: Carga primero islas y temas, y sólo entonces llama a render() ---
    const islas = await api("/islas/");
    islaSelect.innerHTML = islas.map(i =>
      `<option value="${i.id_isla}">${i.id_isla}</option>`
    ).join("");
  
    const temas = await api("/temas/");
    temaList.innerHTML = temas.map(t =>
      `<label class="flex items-center space-x-1">
         <input type="checkbox" class="temaChk" value="${t.id_tema}">
         <span>${t.nombre}</span>
       </label>`
    ).join("");
  
    let current = 0;
    function render() {
      const q = questions[current];
  
      // lateral
      listEl.innerHTML = questions.map((p, i) =>
        `<li data-idx="${i}"
             class="cursor-pointer px-2 py-1 rounded ${i===current?'bg-indigo-200':''}">
           <span class="mr-2 text-indigo-600 font-semibold">${p.id_pregunta}</span>
           ${p.enunciado.slice(0,25)}
         </li>`
      ).join("");
  
      // enunciado
      enunInput.value = q.enunciado || "";
  
      // opciones
      optionList.innerHTML = q.opciones.map((opt, idx) =>
        `<li class="flex items-center space-x-2">
           <button data-idx="${idx}"
                   class="optCorrect px-2 py-1 border rounded ${opt.es_correcta?'bg-green-200':''}">
             ${String.fromCharCode(65+idx)}
           </button>
           <input type="text" data-idx="${idx}"
                  class="flex-1 border px-2 py-1"
                  value="${opt.texto}" />
         </li>`
      ).join("");
  
      // configuraciones
      islaSelect.value = q.id_isla;
      difSelect.value  = q.dificultad;
      randSwitch.checked = q.randomizar;
      vfSwitch.checked   = q.tipo === "vf";
      cbSwitch.checked   = q.tipo === "checkbox";
      // --- Marcar temas correctamente ---
      document.querySelectorAll(".temaChk").forEach(chk => {
        chk.checked = (q.temas || []).includes(Number(chk.value));
      });
    }
  
    // Eventos (puedes dejar igual que ya tienes)
    listEl.addEventListener("click", e => {
      const li = e.target.closest("li[data-idx]");
      if (!li) return;
      current = +li.dataset.idx;
      render();
    });
  
    optionList.addEventListener("click", e => {
      if (!e.target.classList.contains("optCorrect")) return;
      const idx = +e.target.dataset.idx;
      const q = questions[current];
      if (cbSwitch.checked) {
        q.opciones[idx].es_correcta = !q.opciones[idx].es_correcta;
      } else {
        q.opciones.forEach((o,i) => o.es_correcta = i===idx);
      }
      render();
    });
    optionList.addEventListener("input", e => {
      if (e.target.tagName!=="INPUT") return;
      const idx = +e.target.dataset.idx;
      questions[current].opciones[idx].texto = e.target.value;
    });
    addOptBtn.onclick = () => {
      const q = questions[current];
      if (!vfSwitch.checked) {
        q.opciones.push({ texto:"", es_correcta:false });
        render();
      }
    };
    vfSwitch.onchange = () => {
      const q = questions[current];
      if (vfSwitch.checked) {
        cbSwitch.checked = false;
        q.tipo = "vf";
        q.opciones = [
          { texto:"verdadero", es_correcta:false },
          { texto:"falso",     es_correcta:false }
        ];
      } else {
        q.tipo = "abc";
      }
      render();
    };
    cbSwitch.onchange = () => {
      const q = questions[current];
      if (cbSwitch.checked) {
        vfSwitch.checked = false;
        q.tipo = "checkbox";
      } else {
        q.tipo = "abc";
        q.opciones.forEach(o=>o.es_correcta=false);
      }
      render();
    };
    islaSelect.onchange = () => questions[current].id_isla = +islaSelect.value;
    difSelect.onchange  = () => questions[current].dificultad = +difSelect.value;
    randSwitch.onchange = () => questions[current].randomizar = randSwitch.checked;
    temaList.addEventListener("change", () => {
      questions[current].temas =
        [...temaList.querySelectorAll(".temaChk:checked")].map(c=>+c.value);
    });
    enunInput.oninput = () => questions[current].enunciado = enunInput.value;
  
    // 7) Guardado
    async function save(q) {
      if (q.id_pregunta) {
        return api(`/preguntas/${q.id_pregunta}`, { method:"PATCH", body:q });
      } else {
        const saved = await api("/preguntas/", { method:"POST", body:q });
        q.id_pregunta = saved.id_pregunta;
      }
    }
    sendBtn.onclick = async () => {
      await save(questions[current]);
      await api(`/preguntas/${questions[current].id_pregunta}`, {
        method:"PATCH",
        body:{ estado:"en revisión" }
      });
      alert("Enviada a revisión");
    };
    sendAllBtn.onclick = async () => {
      await Promise.all(questions.map(save));
      await api("/preguntas/batch/submit", {
        method:"POST",
        body:{ ids: questions.map(q=>q.id_pregunta) }
      });
      alert("Todas enviadas");
    };
  
    // Render inicial
    render();
  }
  
  
  // ─── PAGE: revisionPreguntas.html ──────────────────────────────────────
  async function initRevision(){
    document.getElementById("logoRevision").onclick=()=>redirect("listadoPreguntas.html");
    document.getElementById("avatarRevision").onclick=()=>redirect("inicio.html");
    let ids=JSON.parse(sessionStorage.getItem("tdSelected")||"[]"); if(!ids.length) return redirect("listadoPreguntas.html");
    const revList=document.getElementById("revList");
    const enunImg=document.getElementById("revEnunImg");
    const enunText=document.getElementById("revEnunText");
    const optsDiv=document.getElementById("revOpts");
    const comment=document.getElementById("revComment");
    const acceptBtn=document.getElementById("acceptBtn");
    const rejectBtn=document.getElementById("rejectBtn");
    const autorAvatar=document.getElementById("revAutorAvatar");
    const autorNombre=document.getElementById("revAutorNombre");
    const autorCargo=document.getElementById("revAutorCargo");
    document.getElementById("viewProfileBtn").onclick=()=>redirect(`verPerfil.html?id=${currentQ.id_profesor}`);
  
    let currentIdx=0; let preguntas=[];
    preguntas=await Promise.all(ids.map(id=>api(`/preguntas/${id}`)));
    renderList(); renderCurrent();
  
    function renderList(){ revList.innerHTML=preguntas.map((p,i)=>`<li data-idx="${i}" class="px-2 py-1 rounded cursor-pointer ${i===currentIdx?"bg-indigo-200":"hover:bg-gray-100"}"><span class="font-semibold text-indigo-600 mr-1">${p.id_pregunta}</span>${p.enunciado.slice(0,30)}</li>`).join(""); }
    function renderCurrent(){ const p=preguntas[currentIdx]; currentQ=p; if(p.url_imagen){enunImg.src=p.url_imagen;enunImg.classList.remove("hidden");enunText.classList.add("hidden");}else{enunText.textContent=p.enunciado;enunText.classList.remove("hidden");enunImg.classList.add("hidden");}
      optsDiv.innerHTML=p.opciones.map(o=>`<div class="px-4 py-2 border rounded text-center ${o.es_correcta?"border-green-400 bg-green-50":"border-red-400 bg-red-50"}">${o.url_imagen?`<img src="${o.url_imagen}" class="max-w-full"/>`:o.texto}</div>`).join("");
      // autor
      api(`/profesores/${p.id_profesor}`).then(pr=>{ if(pr.avatar_url)autorAvatar.src=pr.avatar_url; autorNombre.textContent=`${pr.nombre} ${pr.apellido}`; autorCargo.textContent=pr.cargo||pr.titulo||""; });
    }
    revList.onclick=(e)=>{const li=e.target.closest("li[data-idx]"); if(li){currentIdx=Number(li.dataset.idx); renderList(); renderCurrent();}}
  
    async function decide(dec){ if(dec==="rechazada" && !comment.value.trim()){ alert("Debes escribir un comentario para rechazar."); return; } await api(`/preguntas/${currentQ.id_pregunta}/decision`,{method:"POST",body:{decision:dec,comentario:comment.value||null}}); preguntas.splice(currentIdx,1); ids.splice(currentIdx,1); if(!preguntas.length) return redirect("listadoPreguntas.html"); currentIdx=Math.max(0,currentIdx-1); renderList(); renderCurrent(); comment.value=""; }
    acceptBtn.onclick=()=>decide("aceptada"); rejectBtn.onclick=()=>decide("rechazada");
  }
  
// ─── PAGE: verPerfil.html ────────────────────────────────────────────
async function initProfile(){
    document.getElementById("logoProfile").onclick=()=>redirect("listadoPreguntas.html");
    const params=new URLSearchParams(location.search); const id=params.get("id"); if(!id) return redirect("listadoPreguntas.html");
    const pr=await api(`/profesores/${id}`);
    if(pr.avatar_url) document.getElementById("profAvatar").src=pr.avatar_url;
    document.getElementById("profNombre").textContent=`${pr.nombre} ${pr.apellido}`;
    document.getElementById("profMeta").textContent=`${pr.campus||""} – ${pr.rol==="admin"?"Administrador":"Autor"}`;
    document.getElementById("profCorreo").textContent=pr.correo; document.getElementById("profCorreo").href=`mailto:${pr.correo}`;
    document.getElementById("profTitulo").textContent=pr.titulo||"";
    document.getElementById("profCargo").textContent=pr.cargo||"";
    document.getElementById("profBio").textContent=pr.bio||"";
    // contactar pendiente
  }