let state = { page: 1, page_size: 10, search: "" };

async function fetchBooks() {
  const params = new URLSearchParams({ page: state.page, page_size: state.page_size, search: state.search || "" });
  const res = await fetch(`/api/books?${params.toString()}`);
  if (!res.ok) { alert("Lỗi tải danh sách sách"); return; }
  const json = await res.json();
  renderTable(json);
}

function renderTable(json) {
  const tbody = document.querySelector("#booksTable tbody");
  tbody.innerHTML = "";
  for (const b of json.data) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${b.id}</td>
      <td>${escapeHtml(b.title)}</td>
      <td>${escapeHtml(b.author)}</td>
      <td>${b.isbn ?? ""}</td>
      <td>${b.published_year ?? ""}</td>
      <td>${b.quantity_total ?? 0}</td>
      <td>${b.quantity_available ?? 0}</td>
      <td>
        <button data-id="${b.id}" class="btn-edit">Sửa</button>
        <button data-id="${b.id}" class="btn-del">Xóa</button>
      </td>
    `;
    tbody.appendChild(tr);
  }
  document.getElementById("pageInfo").textContent = `Trang ${json.page} / ${Math.ceil(json.total / json.page_size) || 1}`;

  // bind actions
  document.querySelectorAll(".btn-edit").forEach(btn => btn.addEventListener("click", onEdit));
  document.querySelectorAll(".btn-del").forEach(btn => btn.addEventListener("click", onDelete));
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));
}

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("searchInput");
  const btnSearch = document.getElementById("btnSearch");
  const btnAdd = document.getElementById("btnAdd");
  const prev = document.getElementById("prevPage");
  const next = document.getElementById("nextPage");
  const dialog = document.getElementById("bookDialog");
  const saveBtn = document.getElementById("saveBtn");
  const cancelBtn = document.getElementById("cancelBtn");

  btnSearch.addEventListener("click", () => { state.search = searchInput.value.trim(); state.page = 1; fetchBooks(); });
  btnAdd.addEventListener("click", () => openDialog());
  prev.addEventListener("click", () => { if (state.page > 1) { state.page--; fetchBooks(); }});
  next.addEventListener("click", () => { state.page++; fetchBooks(); });
  cancelBtn.addEventListener("click", () => dialog.close());
  saveBtn.addEventListener("click", onSave);

  if (dialog && typeof dialog.showModal === "function") {
    // ok
  } else {
    alert("Trình duyệt không hỗ trợ dialog modal; form sẽ mở inline.");
  }

  fetchBooks();
});

function openDialog(book) {
  const dialog = document.getElementById("bookDialog");
  document.getElementById("dialogTitle").textContent = book ? "Sửa sách" : "Thêm sách";
  document.getElementById("bookId").value = book?.id ?? "";
  document.getElementById("title").value = book?.title ?? "";
  document.getElementById("author").value = book?.author ?? "";
  document.getElementById("isbn").value = book?.isbn ?? "";
  document.getElementById("published_year").value = book?.published_year ?? "";
  document.getElementById("quantity_total").value = book?.quantity_total ?? 1;
  document.getElementById("quantity_available").value = book?.quantity_available ?? 1;
  document.getElementById("bookDialog").showModal();
}

async function onEdit(e) {
  const id = e.currentTarget.dataset.id;
  const res = await fetch(`/api/books/${id}`);
  if (!res.ok) { alert("Không tải được sách"); return; }
  const b = await res.json();
  openDialog(b);
}

async function onDelete(e) {
  const id = e.currentTarget.dataset.id;
  if (!confirm("Bạn chắc chắn xóa?")) return;
  const res = await fetch(`/api/books/${id}`, { method: "DELETE" });
  if (res.status === 204) {
    fetchBooks();
  } else {
    alert("Xóa thất bại");
  }
}

async function onSave(e) {
  e.preventDefault();
  const id = document.getElementById("bookId").value;
  const payload = {
    title: document.getElementById("title").value.trim(),
    author: document.getElementById("author").value.trim(),
    isbn: document.getElementById("isbn").value.trim() || null,
    published_year: parseInt(document.getElementById("published_year").value || "0") || null,
    quantity_total: parseInt(document.getElementById("quantity_total").value || "0") || 0,
    quantity_available: parseInt(document.getElementById("quantity_available").value || "0") || 0,
  };
  if (!payload.title || !payload.author) { alert("Thiếu tiêu đề hoặc tác giả"); return; }

  const res = await fetch(`/api/books${id ? "/" + id : ""}`, {
    method: id ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (res.ok) {
    document.getElementById("bookDialog").close();
    fetchBooks();
  } else {
    const err = await res.json().catch(()=>({error:"Lỗi không xác định"}));
    alert(err.error || "Lỗi lưu sách");
  }
}
