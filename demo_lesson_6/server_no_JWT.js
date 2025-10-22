const express = require("express");
const app = express();
app.use(express.json());

const USERS = [
    { id: 1, username: "admin", password: "admin123", role: "admin" },
    { id: 2, username: "user", password: "user123", role: "user" },
];

const BOOKS = [
    { id: 1, title: "Clean Code" },
    { id: 2, title: "Designing Data-Intensive Applications" },
];

app.post("/auth/login", (req, res) => {
    const { username, password } = req.body || {};
    const found = USERS.find(u => u.username === username && u.password === password);
    if (!found) return res.status(401).json({ error: "Invalid credentials (no JWT)" });
    return res.json({
        message: "Login OK (no JWT issued)",
        user: { id: found.id, username: found.username, role: found.role }
    });
});

// Public endpoint
app.get("/books", (req, res) => {
    res.json({ data: BOOKS });
});

// Endpoint của riêng admin nhưng không phân quyền (user có thể truy cập vào API của admin)
app.get("/users", (req, res) => {
    const publicUsers = USERS.map(({ id, username, role }) => ({ id, username, role }));
    res.json({ data: publicUsers });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`server running on http://localhost:${PORT}`));