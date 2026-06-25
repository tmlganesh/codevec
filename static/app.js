/**
 * Product Browser - Vanilla JS Frontend
 * Uses offset-based pagination.
 */

const API = "";
const PAGE_SIZE = 20;

// State
let currentPage = 1;
let loading = false;

// DOM elements
const tbody = document.getElementById("tbody");
const categorySelect = document.getElementById("category");
const paginationDiv = document.getElementById("pagination");
const statusDiv = document.getElementById("status");
const errorDiv = document.getElementById("error");
const countSpan = document.getElementById("count");

// --- Init ---
async function init() {
    await loadCategories();
    await loadProducts(1);

    categorySelect.addEventListener("change", () => {
        loadProducts(1);
    });
}

// --- Load categories into dropdown ---
async function loadCategories() {
    try {
        const res = await fetch(`${API}/categories`);
        const categories = await res.json();
        categories.forEach((cat) => {
            const opt = document.createElement("option");
            opt.value = cat;
            opt.textContent = cat;
            categorySelect.appendChild(opt);
        });
    } catch (err) {
        showError("Failed to load categories");
    }
}

// --- Fetch and render products ---
async function loadProducts(page) {
    if (loading) return;
    
    loading = true;
    currentPage = page;
    
    // Smooth transition out
    tbody.style.opacity = '0.5';
    showStatus("Loading...");

    const params = new URLSearchParams({ limit: PAGE_SIZE, page: currentPage });
    const category = categorySelect.value;
    if (category) params.set("category", category);

    try {
        const res = await fetch(`${API}/products?${params}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        
        tbody.innerHTML = "";
        
        data.products.forEach((p) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${escapeHtml(p.name)}</td>
                <td>${escapeHtml(p.category)}</td>
                <td class="price">$${Number(p.price).toFixed(2)}</td>
                <td>${formatDate(p.created_at)}</td>
            `;
            tbody.appendChild(tr);
        });

        if (data.total_count !== undefined) {
            countSpan.textContent = `${data.total_count.toLocaleString()} products total`;
        } else {
            countSpan.textContent = "Please restart your Uvicorn server.";
        }
        
        renderPagination(data.page || 1, data.total_pages || 1);
        
        if (data.products.length === 0) {
            showStatus("No products found.");
        } else {
            hideStatus();
        }
        hideError();
    } catch (err) {
        showError(`Failed to load products: ${err.message}`);
    } finally {
        loading = false;
        // Smooth transition in
        tbody.style.opacity = '1';
    }
}

// --- Render pagination controls ---
function renderPagination(current, total) {
    paginationDiv.innerHTML = "";
    if (total <= 1) return;
    
    // Determine range of pages to show
    let start = Math.max(1, current - 2);
    let end = Math.min(total, current + 2);
    
    // Always show a reasonable window
    if (end - start < 4) {
        if (start === 1) end = Math.min(total, start + 4);
        else if (end === total) start = Math.max(1, end - 4);
    }

    // Previous button
    const prevBtn = document.createElement("button");
    prevBtn.className = "page-btn";
    prevBtn.textContent = "Prev";
    prevBtn.disabled = current === 1;
    prevBtn.onclick = () => loadProducts(current - 1);
    paginationDiv.appendChild(prevBtn);

    // Page numbers
    for (let i = start; i <= end; i++) {
        const btn = document.createElement("button");
        btn.className = `page-btn ${i === current ? 'active' : ''}`;
        btn.textContent = i;
        btn.onclick = () => loadProducts(i);
        paginationDiv.appendChild(btn);
    }

    // Next button
    const nextBtn = document.createElement("button");
    nextBtn.className = "page-btn";
    nextBtn.textContent = "Next";
    nextBtn.disabled = current === total;
    nextBtn.onclick = () => loadProducts(current + 1);
    paginationDiv.appendChild(nextBtn);
}

// --- Helpers ---
function showStatus(msg) {
    statusDiv.textContent = msg;
    statusDiv.style.display = "block";
}

function hideStatus() {
    statusDiv.style.display = "none";
}

function showError(msg) {
    errorDiv.textContent = msg;
    errorDiv.className = "error";
}

function hideError() {
    errorDiv.textContent = "";
    errorDiv.className = "";
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function formatDate(iso) {
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}

// --- Start ---
init();
